from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from profile_app.routing import websocket_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("auth/", include("auth_app.urls")),
    path("accounts/", include("allauth.urls")),
    path("profile/", include("profile_app.urls")),
]
if settings.DEBUG:  # Включать только в режиме разработки
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += websocket_urlpatterns
