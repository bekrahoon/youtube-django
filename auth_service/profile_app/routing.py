from django.urls import re_path
from .consumers import SubscribeConsumer

websocket_urlpatterns = [
    re_path(
        r"^ws/subscribe/(?P<user_id>[^/]+)/(?P<target_user_id>[^/]+)/$",
        SubscribeConsumer.as_asgi(),
    ),
]
