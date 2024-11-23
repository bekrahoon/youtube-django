from comment_app.models import Comment
from comment_app.serializers import CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from comment_service.comment_app.permission import IsOwner


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        elif self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny]
