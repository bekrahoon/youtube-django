from django.forms import ValidationError
from rest_framework import generics
from notification_app.models import Notification
from notification_app.serializers import NotificationSerializer
from .views_get_user_api import get_user_data_from_auth_service


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # Возвращаем уведомления для текущего пользователя
        return Notification.objects.filter(user=self.request.user_id)

    def serializer_valid(self, serializer):
        user_data = get_user_data_from_auth_service(
            self.request.headers.get("Authorization")
        )
        if not user_data:
            raise ValidationError("Неверные данные пользователя.")

        # Передаем user в save() формы
        serializer.save(user=user_data["id"])

        response = super().serializer_valid(serializer)

        return response
