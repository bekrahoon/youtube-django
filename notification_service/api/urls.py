from django.urls import path


from views.views_api import NotificationListView


urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="api_notifications"),
]
