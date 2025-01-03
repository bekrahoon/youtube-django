from django.contrib import admin

from .models import Video, VideoQuality


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "file",
        "preview",
        "duration",
        "processed",
        "created_at",
    )
    list_filter = ("created_at",)


@admin.register(VideoQuality)
class VideoQualityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "video",
        "resolution",
        "file_path",
    )
