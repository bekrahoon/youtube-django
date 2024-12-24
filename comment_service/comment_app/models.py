from django.db import models


class Comment(models.Model):
    user_id = models.IntegerField()
    video_id = models.IntegerField()
    text = models.TextField()
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"video: {self.video_id}, user: {self.user_id}, text: {self.text}"

    class Meta:
        ordering = ["-created_at"]
