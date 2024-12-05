# kafka_consumer.py
from django.utils import timezone
from .models import DeviceToken, Notification
from confluent_kafka import Consumer, KafkaException, KafkaError
from firebase_admin import messaging
import json


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

            if not user_id or not message_text:
                print("Некорректные данные в сообщении.")
                continue
            else:
                print(
                    f"Создание уведомления для user_id={user_id}, текст={message_text}"
                )

            notification = Notification.objects.create(
                user_id=user_id,
                message=message_text,
                starus="unread",
                created_at=timezone.now(),
            )
            print(f"Уведомление создано в БД: {notification}")
            # Отправка push-уведомления через Firebase
            # Предположим, что у вас есть механизм для получения `device_token` по `user_id`.
            device_token = get_device_token(user_id)
            if device_token:
                send_firebase_notification(
                    token=device_token,
                    title="Новое уведомление",
                    body=message_text,
                )
            else:
                print(f"У пользователя с ID {user_id} отсутствует токен устройства.")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


def get_device_token(user_id):
    # Возвращает токен устройства для пользователя с указанным user_id.
    try:
        return DeviceToken.objects.get(user_id=user_id).token
    except DeviceToken.DoesNotExist:
        return None


consume_messages()
from notification_app.models import Notification
from django.utils import timezone
