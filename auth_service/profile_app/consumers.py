from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from auth_app.models import CustomUser
from profile_app.models import Subscription
import json
import logging

logger = logging.getLogger(__name__)


# Асинхронные операции с базой данных
@sync_to_async
def create_subscription(subscriber, subscribed_to):
    return Subscription.objects.create(
        subscriber=subscriber, subscribed_to=subscribed_to
    )


@sync_to_async
def delete_subscription(subscriber, subscribed_to):
    return Subscription.objects.filter(
        subscriber=subscriber, subscribed_to=subscribed_to
    ).delete()


@sync_to_async
def subscription_exists(subscriber, subscribed_to):
    return Subscription.objects.filter(
        subscriber=subscriber, subscribed_to=subscribed_to
    ).exists()


@sync_to_async
def get_followers_count(subscribed_to_id):
    return Subscription.objects.filter(subscribed_to_id=subscribed_to_id).count()


@sync_to_async
def get_user(user_id):
    return get_object_or_404(CustomUser, id=user_id)


class SubscribeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            logger.debug(f"Connect function called with scope: {self.scope}")
            user_id = self.scope["url_route"]["kwargs"]["user_id"]
            target_user_id = self.scope["url_route"]["kwargs"]["target_user_id"]

            logger.info(
                f"User {user_id} connected to subscribe {user_id} -> {target_user_id}"
            )
            self.room_group_name = f"subscription_{user_id}_{target_user_id}"

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
            logger.debug(f"Receive function called with data: {text_data}")
            text_data_json = json.loads(text_data)
            action = text_data_json["action"]
            subscriber_id = text_data_json["subscriber_id"]
            subscribed_to_id = text_data_json["subscribed_to_id"]

            logger.info(
                f"Action received: {action} from {subscriber_id} to {subscribed_to_id}"
            )

            # Получение объектов пользователей
            subscriber = await get_user(subscriber_id)
            subscribed_to = await get_user(subscribed_to_id)

            if action == "subscribe":
                if not await subscription_exists(subscriber, subscribed_to):
                    await create_subscription(subscriber, subscribed_to)
            elif action == "unsubscribe":
                await delete_subscription(subscriber, subscribed_to)

            # Получение обновлённого числа подписчиков
            followers_count = await get_followers_count(subscribed_to_id)

            # Отправка обновления
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "subscription_update",
                    "message": {
                        "action": action,
                        "subscribed_to_id": subscribed_to_id,
                        "followers_count": followers_count,
                    },
                },
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.close()

    async def subscription_update(self, event):
        try:
            logger.debug(f"Subscription update called with event: {event}")
            message = event["message"]
            await self.send(text_data=json.dumps(message))
        except Exception as e:
            logger.error(f"Error in sending subscription update: {str(e)}")
