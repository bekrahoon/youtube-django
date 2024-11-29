from comment_app.serializers import CommentSerializer
from comment_app.permission import IsOwner
from comment_app.models import Comment
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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
