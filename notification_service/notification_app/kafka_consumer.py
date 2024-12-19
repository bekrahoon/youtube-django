# kafka_consumer
from django.conf import settings
from decouple import config
from django.utils import timezone
from confluent_kafka import Consumer, KafkaException, KafkaError
from firebase_admin import messaging
from firebase_admin import credentials
import firebase_admin
import logging
import django
import os
import json

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация Django
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


from .models import DeviceToken, Notification


SERVICE_ACCOUNT_FILE: str = config("FIREBASE_SERVICE_ACCOUNT_KEY")

try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

    logger.info("Firebase успешно инициализирован.")
except Exception as e:
    logger.error(f"Ошибка при инициализации Firebase: {e}")
    raise

# Конфигурация Kafka Consumer
conf = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "notification_group",
    "auto.offset.reset": "latest",
    "debug": "all",  # Включение отладочных логов
}

consumer = Consumer(conf)
topic = "notification-topic"
logger.info("Подписка на Kafka топик...")
consumer.subscribe([topic])
logger.info("Подписка завершена.")


def send_firebase_notification(token, title, body, click_action_url=None):
    """Отправка push-уведомления через Firebase для веб-приложения с картинкой и ссылкой."""

    # Формируем уведомление с дополнительными данными
    notification = messaging.Notification(
        title=title,
        body=body,
        image="static/images/3062634.png",  # Ссылка на изображение
    )

    # Формируем сообщение
    message = messaging.Message(
        notification=notification,
        token=token,
        # Здесь добавляем параметры для web push, например, для ссылки
        webpush=messaging.WebpushConfig(
            fcm_options=messaging.WebpushFCMOptions(  # Исправлено на WebpushFCMOptions
                link=click_action_url
                or "https://your-domain.com/notifications/"  # Ссылка по нажатию
            )
        ),
    )

    try:
        # Отправка сообщения через Firebase
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
                # Попытка декодирования JSON
                message_data = json.loads(message)
                logger.debug(f"Тип данных после json.loads: {type(message_data)}")
                logger.debug(f"Данные сообщения: {message_data}")

                # Проверка, что message_data действительно является строкой JSON
                if isinstance(message_data, str):
                    message_data = json.loads(message_data)
                    logger.debug(
                        f"Тип данных после второго json.loads: {type(message_data)}"
                    )
                    logger.debug(
                        f"Данные сообщения после второго декодирования: {message_data}"
                    )

                # Проверка, что message_data действительно является словарём
                if isinstance(message_data, dict):
                    logger.debug("message_data является словарем.")
                else:
                    logger.error(f"Ожидался словарь, но получено: {type(message_data)}")
                    logger.debug(f"Содержимое message_data: {message_data}")
                    continue

            except json.JSONDecodeError as e:
                logger.error(f"Ошибка при декодировании JSON: {e}")
                continue

            user_id = message_data.get("user_id")
            title = message_data.get("title")
            text_field = message_data.get("text")

            # Обработка text_field (может быть строкой или списком)
            if isinstance(text_field, list):
                message_text = " ".join(map(str, text_field))
            else:
                message_text = str(text_field) if text_field else None
                # Если message_text пуст, используем title
            if not message_text:
                message_text = title

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
            except Exception as e:
                logger.error(f"Ошибка при сохранении уведомления: {e}")
                continue

            # Отправка push-уведомления через Firebase
            device_token = get_device_token(user_id)
            if device_token:
                send_firebase_notification(
                    token=device_token,
                    title=title or "Новое уведомление",
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
        token = DeviceToken.objects.get(user_id=user_id).fcm_token
        logger.debug(f"Получен токен для user_id={user_id}: {token}")
        return token
    except DeviceToken.DoesNotExist:
        logger.warning(f"DeviceToken не найден для user_id={user_id}")
        return None


if __name__ == "__main__":
    consume_messages()
