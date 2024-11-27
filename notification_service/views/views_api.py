from rest_framework import generics
from notification_app.models import Notification
from notification_app.serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # Возвращаем уведомления для текущего пользователя
        return Notification.objects.filter(user=self.request.user)
