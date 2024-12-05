# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from notification_app.consumers import NotificationConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    # Обработка WebSocket соединений
                    path(
                        "ws/notifications/<int:user_id>/",
                        NotificationConsumer.as_asgi(),
                    ),
                ]
            )
        ),
    }
)
