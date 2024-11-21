from rest_framework import serializers, viewsets

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["id", "title", "video_file", "user", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Video.objects.create(user=user, **validated_data)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
