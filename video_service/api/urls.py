from django.urls import include, path

from rest_framework.routers import DefaultRouter
from views.views_api import VideoViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r"video", VideoViewSet, basename="video")

urlpatterns = [
    path("", include(router.urls)),
    path("video/", VideoViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "video/<int:pk>/",
        VideoViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    ),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
