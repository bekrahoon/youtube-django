from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Указываем поля для отображения в административной панели
    list_display = ("email", "username", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "groups")

    # Конфигурируем форму для редактирования пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Конфигурация формы для создания нового пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    search_fields = ("email", "username")
    ordering = ("email",)


# Регистрируем модель CustomUser с кастомной админской конфигурацией
admin.site.register(CustomUser, CustomUserAdmin)
