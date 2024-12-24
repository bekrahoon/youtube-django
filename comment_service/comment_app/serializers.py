from rest_framework.serializers import ModelSerializer
from comment_app.models import Comment


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "user_id",
            "video_id",
            "text",
            "created_at",
        ]
