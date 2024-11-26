from comment_app.models import Comment
from comment_app.serializers import CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from comment_app.permission import IsOwner


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]  # Устанавливаем базовое разрешение

    def get_permissions(self):
        # Динамическая логика для разрешений
        if self.action in ["update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        elif self.action == "create":
            return [IsAuthenticated()]
        elif self.action == "post":
            return [IsAuthenticated()]
        # Для других действий используем базовое разрешение AllowAny
        return [AllowAny()]