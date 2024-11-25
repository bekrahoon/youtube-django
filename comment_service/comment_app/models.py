from django.db import models


class Comment(models.Model):
    user_id = models.IntegerField()
    video_id = models.IntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"video: {self.video.id}, user: {self.user.id}, text: {self.text}"

    class Meta:
        ordering = ["-created_at"]
