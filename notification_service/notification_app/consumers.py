import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from notification_app.models import Notification
from notification_app.serializers import NotificationSerializer
from django.contrib.auth import get_user_model  # Импорт кастомной модели пользователя

User = get_user_model()


# Настроим логирование
logger = logging.getLogger(__name__)


# Асинхронные операции с базой данных
@sync_to_async
def create_notification(user, message):
    # Создаём уведомление в базе данных
    return Notification.objects.create(user=user, message=message, status="unread")


@sync_to_async
def get_notifications(user):
    # Получаем уведомления для пользователя
    return Notification.objects.filter(user=user)


@sync_to_async
def update_notification_status(notification_id):
    # Обновляем статус уведомления на "прочитано"
    notification = Notification.objects.get(id=notification_id)
    notification.status = "read"
    notification.save()


@sync_to_async
def get_user(user_id):
    # Получаем пользователя
    return User.objects.get(id=user_id)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Получаем user_id из URL
            user_id = self.scope["url_route"]["kwargs"]["user_id"]
            self.user = await get_user(user_id)

            logger.info(f"User {self.user.id} connected to notifications.")
            self.room_group_name = f"notifications_{self.user.id}"

            # Присоединяемся к группе
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name,
            )

            await self.accept()
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close()

    async def receive(self, text_data):
        try:
            # Обработка полученных данных
            text_data_json = json.loads(text_data)
            action = text_data_json["action"]

            logger.info(f"Received action: {action} from user {self.user.id}")

            if action == "get_notifications":
                notifications = await get_notifications(self.user)
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
            logger.error(f"Error in receive: {str(e)}")
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
            logger.error(f"Error in notification_status_update: {str(e)}")

    async def disconnect(self, close_code):
        try:
            # Отключаем пользователя от группы
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")
            await self.close()
