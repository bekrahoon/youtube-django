from django.db import models
from auth_app.models import CustomUser


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(max_length=500, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def followers(self):
        return CustomUser.objects.filter(subscriptions__subscribed_to=self.user)


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="subscriptions"
    )
    subscribed_to = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="subscribers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.subscriber.username} is subscribed to {self.subscribed_to.username}"
        )
