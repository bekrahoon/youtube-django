from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",  # Уникальное имя для обратной ссылки
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",  # Уникальное имя для обратной ссылки
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
