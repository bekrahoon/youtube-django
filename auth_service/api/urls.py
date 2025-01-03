from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from views.profile_api import UserProfileViewSet
from views.views_api import LoginView, RegisterView, UserInfoView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"profiles", UserProfileViewSet, basename="profile")

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    # Регистрация и вход пользователя
    path("auth/", obtain_auth_token),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    # Включаем маршруты из DefaultRouter для профилей пользователей
    path("", include(router.urls)),
    path("user-info/", UserInfoView.as_view(), name="user_info"),
]
