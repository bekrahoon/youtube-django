from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from views.views import (
    LiveStreamView,
    StreamVideoView,
    TranscodeVideoView,
    VideoListView,
    VideoCreateView,
    VideoUpdateView,
    VideoDeleteView,
    VideoDetailView,
)


urlpatterns = [
    path("", VideoListView.as_view(), name="video_list"),  # Список видео
    path("detail/<int:pk>", VideoDetailView.as_view(), name="video_detail"),
    path("create/", VideoCreateView.as_view(), name="video_create"),  # Создание видео
    path(
        "update/<int:pk>/", VideoUpdateView.as_view(), name="video_update"
    ),  # Обновление видео
    path(
        "delete/<int:pk>/", VideoDeleteView.as_view(), name="video_delete"
    ),  # Удаление видео
    path("stream/<int:pk>/", StreamVideoView.as_view(), name="stream_video"),
    path(
        "transcode/<int:pk>/",
        TranscodeVideoView.as_view(),
        name="transcode_video",
    ),
    path("live/", LiveStreamView.as_view(), name="live_stream"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
