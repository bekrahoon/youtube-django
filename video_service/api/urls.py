from django.urls import include, path

from rest_framework.routers import DefaultRouter
from views.views_api import VideoViewSet

router = DefaultRouter()
router.register(r"video", VideoViewSet, basename="video")

urlpatterns = [
    path("", include(router.urls)),
    path("video/", VideoViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "video/<int:pk>/",
        VideoViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    ),
]
