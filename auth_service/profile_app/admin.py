from django.contrib import admin

from .models import Subscription, UserProfile


@admin.register(UserProfile)
class ProfileUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "bio",
        "location",
        "birth_date",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "location", "bio")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    # Настройка для отображения полей редактирования
    fieldsets = (
        (
            None,
            {"fields": ("user", "bio", "avatar", "location", "birth_date")},
        ),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Subscription)
class ProfileUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subscriber",
        "subscribed_to",
        "created_at",
    )
    search_fields = ("subscriber", "subscribed_to")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
