from django.urls import path

from views.profile import UserProfileDetailView, UserProfileUpdateView

app_name = "profile_app"

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
