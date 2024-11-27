from django.utils import timezone
from django.contrib.auth import get_user_model  # Импорт кастомной модели пользователя
from .models import Notification
from confluent_kafka import Consumer, KafkaException, KafkaError
import json

# Получаем модель пользователя
User = get_user_model()

# Конфигурация Kafka Consumer
conf = {
    "bootstrap.servers": "localhost:9092",  # Адрес Kafka сервера
    "group.id": "notification_group",  # ID группы для Consumer
    "auto.offset.reset": "earliest",  # Начать с первого сообщения, если нет смещения
}

# Создание Kafka Consumer
consumer = Consumer(conf)

# Подписка на топик
topic = "notification-topic"
consumer.subscribe([topic])


# Функция для получения сообщений и сохранения уведомлений
def consume_messages():
    try:
        while True:
            msg = consumer.poll(1.0)  # 1 секунда ожидания сообщения
            if msg is None:
                continue  # Нет сообщений
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Конец раздела, ничего не делать
                    continue
                else:
                    raise KafkaException(msg.error())
            # Обработка полученного сообщения
            message = msg.value().decode("utf-8")
            print(f"Получено сообщение: {message}")
            # Преобразование сообщения в формат JSON
            message_data = json.loads(message)
            user_id = message_data.get("user_id")
            message_text = message_data.get("text")

            # Проверка существования пользователя
            try:
                user = User.objects.get(id=user_id)
                # Создание уведомления
                notification = Notification.objects.create(
                    user=user,
                    message=message_text,
                    status="unread",
                    created_at=timezone.now(),
                )
                print(f"Уведомление создано: {notification}")
            except User.DoesNotExist:
                print(f"Пользователь с ID {user_id} не найден.")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


# Вызов функции для получения сообщений
consume_messages()
