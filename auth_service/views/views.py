from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken
from auth_app.forms import CustomRegisterForm, CustomLoginForm
from profile_app.models import UserProfile
from confluent_kafka import Producer
import json

# Настройка Kafka
kafka_conf = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "auth-topic",
}

producer = Producer(kafka_conf)


def delivery_callback(err, msg):
    if err is not None:
        print(f"ОШИБКА: {err}")
    else:
        print(f"Сообщение {msg.topic()}[{msg.partition()}] доставлено успешно.")


# Отправка сообщения в Kafka
def send_to_comment_service(topic, message):
    try:
        producer.produce(
            topic,
            key="user_event",
            value=json.dumps(message),
            callback=delivery_callback,
        )
        producer.flush()
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Kafka: {e}")


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
            messages.success(request, "Registration successful")

            # Отправляем информацию о новом пользователе в comment_service через Kafka
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "action": "register",
            }
            send_to_comment_service("comment-topic", user_data)

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
            messages.success(request, "Login successful")

            # Отправляем информацию о пользователе в comment_service через Kafka
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "action": "login",
            }
            send_to_comment_service("comment-topic", user_data)

            # Перенаправляем на страницу профиля пользователя
            return redirect("profile_app:profile_detail", pk=user.id)

        messages.error(request, "Login failed, please try again")
        return render(request, "auth_app/login.html", {"form": form})
