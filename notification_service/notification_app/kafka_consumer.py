from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Notification
from confluent_kafka import Consumer, KafkaException, KafkaError
from firebase_admin import messaging
import json

User = get_user_model()

# Конфигурация Kafka Consumer
conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "notification_group",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)
topic = "notification-topic"
consumer.subscribe([topic])


def send_firebase_notification(token, title, body):
    """Отправка push-уведомления через Firebase."""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    response = messaging.send(message)
    print(f"Push-уведомление отправлено: {response}")


def consume_messages():
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            message = msg.value().decode("utf-8")
            print(f"Получено сообщение: {message}")
            message_data = json.loads(message)
            user_id = message_data.get("user_id")
            message_text = message_data.get("text")

            try:
                user = User.objects.get(id=user_id)
                # Создание уведомления в базе данных
                notification = Notification.objects.create(
                    user=user,
                    message=message_text,
                    status="unread",
                    created_at=timezone.now(),
                )
                print(f"Уведомление создано: {notification}")

                # Отправка push-уведомления через Firebase
                if hasattr(
                    user, "device_token"
                ):  # Убедитесь, что у пользователя есть токен устройства
                    send_firebase_notification(
                        token=user.device_token,
                        title="Новое уведомление",
                        body=message_text,
                    )
                else:
                    print(f"У пользователя {user_id} отсутствует токен устройства.")
            except User.DoesNotExist:
                print(f"Пользователь с ID {user_id} не найден.")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


consume_messages()
