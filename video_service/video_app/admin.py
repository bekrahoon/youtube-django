from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "file",
        "duration",
        "created_at",
        "status",
    )
    list_filter = ("created_at",)
