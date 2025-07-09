from django.views.generic import DetailView, UpdateView
from django.urls import reverse
from profile_app.forms import UserProfileForm
from profile_app.models import UserProfile
from rest_framework_simplejwt.authentication import JWTAuthentication
from profile_app.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated


class UserProfileDetailView(DetailView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]
    model = UserProfile
    template_name = "user_profile_app/profile_detail.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class UserProfileUpdateView(UpdateView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]
    model = UserProfile
    form_class = UserProfileForв
    template_name = "user_profile_app/profile_edit.html"
    success_url = "/profile/{pk}/"

    def get_success_url(self):
        return reverse("profile_app:profile_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.object  # Передаём объект профиля в контекст
        return context
