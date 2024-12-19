from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Video(models.Model):
    user = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=100, null=True, blank=True
    )  # Простая категория
    tags = models.JSONField()
    keywords = models.TextField(
        max_length=100, null=True, blank=True
    )  # Ключевые слова через запятую
    file = models.FileField(upload_to="videos/")
    preview = models.ImageField(upload_to="preview/")
    duration = models.DurationField(null=True, blank=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class VideoQuality(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="qualities")
    resolution = models.CharField(max_length=10)  # пример, '360p', '720p'
    file_path = models.FileField(upload_to="video/")
