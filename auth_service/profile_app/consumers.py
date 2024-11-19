import json
from channels.generic.websocket import AsyncWebsocketConsumer
from auth_app.models import CustomUser
from profile_app.models import Subscription


class SubscribeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "subcribtion_group"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json("action")
        subscriber_id = text_data_json("subscriber_id")
        subscribed_to_id = text_data_json("subscribed_to_id")

        if action == "subscribe":
            # Логика для подписки
            subscriber = CustomUser.objects.get(id=subscriber_id)
            subscribed_to = CustomUser.objects.get(id=subscribed_to_id)
            Subscription.objects.filter(
                subscriber=subscriber, subscribed_to=subscribed_to
            )
        elif action == "unsubscribe":
            subscriber = CustomUser.objects.get(id=subscriber_id)
            subscribed_to = CustomUser.objects.get(id=subscribed_to_id)
            Subscription.objects.filter(
                subscriber=subscriber, subscribed_to=subscribed_to
            ).delete
        followers_count = Subscription.objects.filter(
            subscribed_to_id=subscribed_to_id
        ).count()
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

    async def subscription_update(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
