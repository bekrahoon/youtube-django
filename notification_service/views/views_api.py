from rest_framework import generics
from notification_app.models import Notification
from notification_app.serializers import NotificationSerializer
from .views_get_user_api import get_user_data_from_auth_service
from rest_framework.permissions import AllowAny

from rest_framework.exceptions import AuthenticationFailed


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Проверка токена и получение данных пользователя
        token = self.request.headers.get("Authorization")
        user_data = get_user_data_from_auth_service(token)
        if not user_data:
            raise AuthenticationFailed("Неверные данные пользователя.")

        # Привязываем ID пользователя к запросу
        self.request.user_id = int(user_data["id"])

        # Возвращаем уведомления для пользователя
        return Notification.objects.filter(user_id=self.request.user_id)
