from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from video_app.models import Video
from video_app.serializers import VideoSerializer
from confluent_kafka import Producer

from video_app.permissions import IsOwner


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print(f"User from request: {self.request.user}")
        video = serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ["update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]
