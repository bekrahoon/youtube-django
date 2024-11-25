from django.urls import include, path

from rest_framework.routers import DefaultRouter
from views.views_api import CommentViewSet

router = DefaultRouter()
router.register(r"comment", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
    path("comment/", CommentViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "comment/<int:pk>/",
        CommentViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
    ),
]
