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
    path("create/", VideoCreateView.as_view(), name="video_create"),  # Создание видео
    path(
        "update/<int:pk>/", VideoUpdateView.as_view(), name="video_update"
    ),  # Обновление видео
    path(
        "delete/<int:pk>/", VideoDeleteView.as_view(), name="video_delete"
    ),  # Удаление видео
    path("stream/<int:video_id>/", StreamVideoView.as_view(), name="stream_video"),
    path(
        "transcode/<int:video_id>/",
        TranscodeVideoView.as_view(),
        name="transcode_video",
    ),
    path("live/", LiveStreamView.as_view(), name="live_stream"),
    path("detail/<int:pk>", VideoDetailView.as_view(), name="video_detail"),
]
