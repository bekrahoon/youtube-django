from django.urls import path

from views.firebase_notic import SaveFcmTokenView, showFirebaseJS
from views.views import NotificationsView, MarkAsReadView

urlpatterns = [
    path("notifications/", NotificationsView.as_view(), name="notifications"),
    path(
        "notifications/mark_as_read/<int:id>/",
        MarkAsReadView.as_view(),
        name="mark_as_read",
    ),
    path(
        "firebase-messaging-sw.js",
        showFirebaseJS,
        name="show_firebase_js",
    ),
    path(
        "notifications/save-fcm-token/",
        SaveFcmTokenView.as_view(),
        name="save_fcm_token",
    ),  # Маршрут для сохранения FCM токена
]
