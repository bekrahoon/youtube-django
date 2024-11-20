from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken
from auth_app.forms import CustomRegisterForm, CustomLoginForm
from profile_app.models import UserProfile
from confluent_kafka import Producer, KafkaException
from rest_framework.response import Response

# Настройка логирования
# logger = logging.getLogger(__name__)  # Не нужно, если используем print

kafka_conf = {
    "bootstrap.servers": "kafka:9092",  # Используйте имя контейнера Kafka в сети Docker
    "client.id": "auth-topic",
}

producer = Producer(kafka_conf)


def delivery_callback(err, msg):
    if err is not None:
        print(f"ОШИБКА: {err}")  # Замените на print
    else:
        print(
            f"Сообщение {msg.topic()}[{msg.partition()}] доставлено успешно."
        )  # Замените на print


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

            # Проверка подключения к Kafka
            try:
                producer.produce(
                    "test-topic", key="test", value="test", callback=delivery_callback
                )
                producer.flush()
                print("Подключение к Kafka успешно!")
            except KafkaException as e:
                print(f"Ошибка при подключении к Kafka: {e}")

            # Отправка сообщения в Kafka о регистрации пользователя
            registretion_message = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
            }
            try:
                producer.produce(
                    "user-registered-topic",
                    key="user_registered",
                    value=str(registretion_message),
                    callback=delivery_callback,
                )
                producer.flush()
                print(
                    "Сообщение о регистрации пользователя успешно отправлено в Kafka."
                )
            except KafkaException as e:
                print(f"Ошибка при отправке сообщения в Kafka: {e}")

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            messages.success(request, "Registration successful")

            # Логируем ID пользователя перед редиректом
            print(f"Redirecting to profile with ID: {user.id}")

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

            # Проверка подключения к Kafka
            try:
                producer.produce(
                    "test-topic", key="test", value="test", callback=delivery_callback
                )
                producer.flush()
                print("Подключение к Kafka успешно!")  # Замените на print
            except KafkaException as e:
                print(f"Ошибка при подключении к Kafka: {e}")  # Замените на print

            # Отправка сообщения в Kafka о входе пользователя
            login_message = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
            }
            try:
                producer.produce(
                    "user-loged-in-topik",
                    key="user_loged_in",
                    value=str(login_message),
                    callback=delivery_callback,
                )
                print(
                    "Сообщение о входе пользователя успешно отправлено в Kafka."
                )  # Замените на print
            except KafkaException as e:
                print(
                    f"Ошибка при отправке сообщения в Kafka: {e}"
                )  # Замените на print

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            messages.success(request, "Login successful")
            return redirect("profile_app:profile_detail", pk=user.id)
        messages.error(request, "Login failed, please try again")
        return render(request, "auth_app/login.html", {"form": form})
