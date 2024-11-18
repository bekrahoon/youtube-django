from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from video_app.models import Video
from video_app.serializers import VideoSerializer
from confluent_kafka import Producer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        video = serializer.save(user=self.request.user)
        # Отправка сообщения в Kafka после загрузки видео
        producer = Producer(bootstrap_servers=["localhost:9092"])
        producer.send("video_topic", b"New video uploaded: %s" % video.id)
        producer.flush()
