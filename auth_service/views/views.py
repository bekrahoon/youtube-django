from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken
from auth_app.forms import CustomRegisterForm, CustomLoginForm
from profile_app.models import UserProfile


class RegisterView(View):
    def get(self, request):
        form = CustomRegisterForm()
        return render(request, "auth_app/register.html", {"form": form})

    def post(self, request):
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)

            # Указываем backend для логина через строку пути
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Устанавливаем токен в куку
            response = redirect("profile_app:profile_detail", pk=user.id)
            response.set_cookie("access_token", access_token, httponly=False)

            messages.success(request, "Registration successful")
            return response

        return render(request, "auth_app/register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()
        return render(request, "auth_app/login.html", {"form": form})

    def post(self, request):
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Указываем backend для логина через строку пути
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Устанавливаем токен в куку
            response = redirect("profile_app:profile_detail", pk=user.id)
            response.set_cookie("access_token", access_token, httponly=False)

            messages.success(request, "Login successful")
            return response

        messages.error(request, "Login failed, please try again")
        return render(request, "auth_app/login.html", {"form": form})
