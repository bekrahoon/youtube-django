from django.urls import path
from views.views import NotificationsView, MarkAsReadView

urlpatterns = [
    path("notifications/", NotificationsView.as_view(), name="notifications"),
    path(
        "notifications/mark_as_read/<int:id>/",
        MarkAsReadView.as_view(),
        name="mark_as_read",
    ),
]
