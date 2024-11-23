from rest_framework.serializers import ModelSerializer
from comment_app.models import Comment


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "video",
            "text",
            "created_at",
        ]
