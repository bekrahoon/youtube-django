import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from profile_app import routing as profile_routing


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_project.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                profile_routing.websocket_urlpatterns,
            ),
        ),
    }
)
