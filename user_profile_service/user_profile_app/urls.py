from django.urls import path

from views.views import UserProfileDetailView, UserProfileUpdateView

app_name = "user_profile_app"

urlpatterns = [
    path(
        "<int:pk>/",
        UserProfileDetailView.as_view(),
        name="profile_detail",
    ),
    path(
        "<int:pk>/edit/",
        UserProfileUpdateView.as_view(),
        name="profile_edit",
    ),
]
