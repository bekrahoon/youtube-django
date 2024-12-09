import os
import django
import logging
from django.conf import settings

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Настройка Django
if not settings.configured:
    logger.info("Django не был инициализирован. Инициализация Django...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification_service.settings")
    try:
        django.setup()
        logger.info("Django успешно инициализирован.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации Django: {e}")
else:
    logger.debug("Django уже инициализирован.")


from django.utils import timezone
from confluent_kafka import Consumer, KafkaException, KafkaError
from firebase_admin import messaging
import json

from .models import DeviceToken, Notification


# Конфигурация Kafka Consumer
conf = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "notification_group",
    "auto.offset.reset": "earliest",
    "debug": "all",  # Включение отладочных логов
}

consumer = Consumer(conf)
topic = "notification-topic"
logger.info("Подписка на Kafka топик...")
consumer.subscribe([topic])
logger.info("Подписка завершена.")


def send_firebase_notification(token, title, body):
    """Отправка push-уведомления через Firebase."""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        logger.info(f"Push-уведомление отправлено: {response}")
    except Exception as e:
        logger.error(f"Ошибка при отправке push-уведомления: {e}")


def consume_messages():
    print("Kafka Consumer запущен")
    logger.info("Запуск Kafka Consumer...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                logger.debug("Нет новых сообщений от Kafka.")
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug("Достигнут конец партиции Kafka.")
                    continue
                else:
                    raise KafkaException(msg.error())

            # Декодирование и логирование сообщения
            message = msg.value().decode("utf-8")
            logger.info(f"Получено сообщение из Kafka: {message}")

            try:
                # Проверка, если данные уже строка JSON
                if isinstance(message, str):
                    message_data = json.loads(message)
                    logger.debug(f"Данные сообщения: {message_data}")
                else:
                    logger.error(f"Сообщение не является строкой JSON: {message}")
                    continue
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка при декодировании JSON: {e}")
                continue

            # Теперь проверка, что message_data действительно является словарём
            if not isinstance(message_data, dict):
                logger.error(f"Ожидался словарь, но получено: {type(message_data)}")
                continue

            user_id = message_data.get("user_id")
            message_text = message_data.get("title" or "text")

            if not user_id or not message_text:
                logger.warning("Некорректные данные в сообщении. Пропуск.")
                continue

            logger.info(
                f"Создание уведомления для user_id={user_id}, текст={message_text}"
            )

            # Сохранение уведомления в базе данных
            try:
                notification = Notification.objects.create(
                    user_id=user_id,
                    message=message_text,
                    status="unread",
                    created_at=timezone.now(),
                )
                logger.info(f"Уведомление добавлено в БД: {notification}")
                logger.debug(f"Содержимое уведомления: {notification}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении уведомления: {e}")
                continue

            # Отправка push-уведомления через Firebase
            device_token = get_device_token(user_id)
            if device_token:
                send_firebase_notification(
                    token=device_token,
                    title="Новое уведомление",
                    body=message_text,
                )
            else:
                logger.warning(
                    f"Токен устройства не найден для пользователя с ID {user_id}"
                )

    except KeyboardInterrupt:
        logger.info("Работа потребителя завершена.")
    finally:
        consumer.close()


def get_device_token(user_id):
    """Возвращает токен устройства для пользователя с указанным user_id."""
    try:
        token = DeviceToken.objects.get(user_id=user_id).token
        logger.debug(f"Получен токен для user_id={user_id}: {token}")
        return token
    except DeviceToken.DoesNotExist:
        logger.warning(f"DeviceToken не найден для user_id={user_id}")
        return None


consume_messages()
