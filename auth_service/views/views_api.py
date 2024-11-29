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
            # Создаем пользователя
            user = form.save()
            UserProfile.objects.create(user=user)

            # Авторизуем пользователя после регистрации
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # Генерация JWT токена
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Сохраняем токен в сессии или передаем в контексте
            request.session["access_token"] = str(access_token)
            messages.success(request, "Registration successful")

            # Перенаправляем на страницу профиля пользователя
            return redirect("profile_app:profile_detail", pk=user.id)

        # Если форма не прошла валидацию, возвращаем обратно с ошибками
        return render(request, "auth_app/register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()
        return render(request, "auth_app/login.html", {"form": form})

    def post(self, request):
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Генерация JWT токена
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Сохраняем токен в сессии или передаем в контексте
            request.session["access_token"] = str(access_token)
            messages.success(request, "Login successful")

            # Перенаправляем на страницу профиля пользователя
            return redirect("profile_app:profile_detail", pk=user.id)

        messages.error(request, "Login failed, please try again")
        return render(request, "auth_app/login.html", {"form": form})
