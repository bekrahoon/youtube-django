from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from video_app.models import Video
from video_app.serializers import VideoSerializer
from confluent_kafka import Producer

from video_app.permissions import IsOwner

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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print(f"Пользователь из запроса: {self.request.user}")
        video = serializer.save(user=self.request.user)
        # Отправка сообщения в Kafka при создании видео
        send_kafka_message(
            topic="video_events",
            key="video created",
            value=f"Video created: {video.title} by {video.user.username}",
        )

    def perform_update(self, serializer):
        print(f"Пользователь из запроса: {self.request.user}")
        video = serializer.save()
        # Отправка сообщения в Kafka при обновлении видео
        send_kafka_message(
            topic="video_events",
            key="video updated",
            value=f"Video updated: {video.title} by {video.user.username}",
        )

    def perform_destroy(self, instance):
        video_title = instance.title
        video_user = instance.user.username
        instance.delete()
        # Отправка сообщения в Kafka при удалении видео
        send_kafka_message(
            topic="video_events",
            key="video destroyd",
            value=f"Video destroyd: {video_title} by {video_user}",
        )

    def get_permissions(self):
        if self.action in ["update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]
