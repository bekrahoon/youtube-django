from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Video(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="videos"
    )  # Связь с пользователем из auth_service

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="videos/")
    preview = models.ImageField(upload_to="preview/")
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, default="uploaded"
    )  # uploaded, processing, completed

    def __str__(self):
        return self.title
