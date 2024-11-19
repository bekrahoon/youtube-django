from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/subscribe/", consumers.SubscribeConsumer.as_asgi()),
]
