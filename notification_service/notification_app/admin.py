from django.contrib import admin

from .models import DeviceToken, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "message", "status", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user_id", "message")


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "token", "created_at", "updated_at")
