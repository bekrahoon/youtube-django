# consumer.py
import json
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Notification
from .serializers import NotificationSerializer

from views.views_get_user_api import get_user_data_from_auth_service


# Асинхронные операции с базой данных
@sync_to_async
def create_notification(user_id, message):
    return Notification.objects.create(
        user_id=user_id, message=message, status="unread"
    )


@sync_to_async
def get_notifications(user_id):
    return Notification.objects.filter(user_id=user_id)


@sync_to_async
def update_notification_status(notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.status = "read"
    notification.save()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Получаем токен из заголовков запроса
            token = self.scope["headers"].get("authorization", None)
            if not token:
                await self.close()  # Закрыть соединение, если нет токена
                return

            # Получаем данные пользователя из auth_service
            user_data = await sync_to_async(get_user_data_from_auth_service)(token)
            if not user_data:
                await self.close()  # Закрыть соединение, если данные не найдены
                return

            self.user_id = user_data["id"]
            self.room_group_name = f"notifications_{self.user_id}"

            # Присоединяемся к группе
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name,
            )

            await self.accept()

        except Exception as e:
            print(f"Error in connect: {str(e)}")
            await self.close()

    async def receive(self, text_data):
        try:
            # Обработка полученных данных
            text_data_json = json.loads(text_data)
            action = text_data_json["action"]

            if action == "get_notifications":
                notifications = await get_notifications(self.user_id)
                notifications_data = NotificationSerializer(
                    notifications, many=True
                ).data

                # Отправляем уведомления в WebSocket
                await self.send(
                    text_data=json.dumps(
                        {"type": "notifications", "notifications": notifications_data}
                    )
                )

            elif action == "mark_read":
                notification_id = text_data_json["notification_id"]
                await update_notification_status(notification_id)

                # Отправка обновления о статусе уведомления
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "notification_status_update",
                        "notification_id": notification_id,
                        "status": "read",
                    },
                )
        except Exception as e:
            print(f"Error in receive: {str(e)}")
            await self.close()

    async def notification_status_update(self, event):
        try:
            # Отправляем статус обновления
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "notification_status_update",
                        "notification_id": event["notification_id"],
                        "status": event["status"],
                    }
                )
            )
        except Exception as e:
            print(f"Error in notification_status_update: {str(e)}")

    async def disconnect(self, close_code):
        try:
            # Отключаем пользователя от группы
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )
        except Exception as e:
            print(f"Error in disconnect: {str(e)}")
            await self.close()
