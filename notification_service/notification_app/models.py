from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    STATUS_CHOICES = {
        ("unread", "Unread"),
        ("read", "Read"),
        ("archived", "Archived"),
    }

    user_id = models.IntegerField()
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unread")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user_id} - {self.status}"


class DeviceToken(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=255, unique=True)  # Сделаем токен уникальным
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token for User ID {self.user_id}"
