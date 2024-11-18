from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from profile_app.forms import UserProfileForm
from profile_app.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin


class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = "user_profile_app/profile_detail.html"
    context_object_name = "profile"


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "user_profile_app/profile_edit.html"
    success_url = "/profile/{pk}/"

    def get_success_url(self):
        return reverse("profile_app:profile_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.object  # Передаём объект профиля в контекст
        return context
