from django.urls import path
from .consumers import LiveStreamConsumer

websocket_urlpatterns = [
    path("ws/live/", LiveStreamConsumer.as_asgi()),
]
