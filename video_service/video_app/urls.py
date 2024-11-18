# video_app/urls.py
from django.urls import path
from views.views import VideoListView, VideoCreateView, VideoUpdateView, VideoDeleteView

urlpatterns = [
    path("", VideoListView.as_view(), name="video_list"),  # Список видео
    path("create/", VideoCreateView.as_view(), name="video_create"),  # Создание видео
    path(
        "update/<int:pk>/", VideoUpdateView.as_view(), name="video_update"
    ),  # Обновление видео
    path(
        "delete/<int:pk>/", VideoDeleteView.as_view(), name="video_delete"
    ),  # Удаление видео
]
