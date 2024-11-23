from django.db import models

from auth_service.auth_app.models import CustomUser
from video_service.video_app.models import Video


class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"video: {self.video.id}, user: {self.user.id}, text: {self.text}"

    class Meta:
        ordering = ["-created_at"]
