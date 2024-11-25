from comment_app.models import Comment
from comment_app.serializers import CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from comment_app.permission import IsOwner


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = JWTAuthentication

    def get_permissions(self):
        if self.action in ["update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        elif self.action in ["create"]:
            return [IsAuthenticated()]
        return [AllowAny]
