from video_app.serializers import VideoSerializer
from video_app.permissions import IsOwner
from video_app.models import Video
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from confluent_kafka import Producer
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from .views_get_user_api import get_user_data_from_auth_service

kafka_config = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "video-topic",
}  # Укажите ваш адрес Kafka сервера
producer = Producer(kafka_config)


def send_kafka_message(topic, key, value):
    try:
        producer.produce(topic, key=key, value=value)
        producer.flush()
        print(f"Сообщение, отправленное в тему Kafka: '{topic}'")
    except Exception as e:
        print(f"Не удалось отправить сообщение в тему Kafka: {e}")


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = []  # Если не используете стандартную аутентификацию
    permission_classes = [AllowAny]

    def get_permissions(self):
        # Применение разрешений только для действий update и destroy
        if self.action in ["update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Получаем токен из заголовка запроса
        token = self.request.headers.get("Authorization")
        user_data = get_user_data_from_auth_service(token)
        if not user_data:
            raise AuthenticationFailed("Неверные данные пользователя.")

        # Сохраняем видео и отправляем сообщение в Kafka
        video = serializer.save(user_id=user_data["id"])
        send_kafka_message(
            topic="video-topic",
            key="video created",
            value=f"Video created: {video.title} by {video.user.username}",
        )

    def perform_update(self, serializer):
        # Проверка данных пользователя и обновление видео
        token = self.request.headers.get("Authorization")
        user_data = get_user_data_from_auth_service(token)
        if not user_data:
            raise AuthenticationFailed("Неверные данные пользователя.")

        video = serializer.save()
        send_kafka_message(
            topic="video-topic",
            key="video updated",
            value=f"Video updated: {video.title} by {video.user.username}",
        )

    def perform_destroy(self, instance):
        # Удаление видео и отправка сообщения в Kafka
        video_title = instance.title
        video_user = instance.user.username
        instance.delete()
        send_kafka_message(
            topic="video-topic",
            key="video destroyed",
            value=f"Video destroyed: {video_title} by {video_user}",
        )
