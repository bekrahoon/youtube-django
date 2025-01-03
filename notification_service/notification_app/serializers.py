from rest_framework import serializers
from notification_app.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user_id", "message", "status", "created_at"]
