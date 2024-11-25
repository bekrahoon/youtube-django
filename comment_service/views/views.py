import json
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from comment_app.models import Comment
from comment_app.forms import CommentForm
from comment_app.kafka_producer import KafkaProducer
from comment_app.kafka_consumer import (
    get_video_data,
)


class CommentViewList(ListView):
    model = Comment
    template_name = "comment_app/comment_list.html"
    context_object_name = "comments"
    queryset = Comment.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_with_details = []

        for comment in self.queryset:
            # Извлечение данных пользователя из JWT-токена
            user_token = self.request.headers.get("Authorization", "").split("Bearer ")[
                -1
            ]
            user_data = get_user_data_from_token(user_token)

            # Получение данных о видео через Kafka
            video_data = get_video_data(comment.video_id)

            comments_with_details.append(
                {
                    "comment": comment,
                    "user": user_data,
                    "video": video_data,
                }
            )

        context["comments_with_details"] = comments_with_details
        context["comment"] = "Список комментариев"
        return context


class CommentPostView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment_app/comment_post.html"
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Отправка уведомления в Kafka
        producer = KafkaProducer()
        topic = "notification-topic"
        message = {
            "comment_id": self.object.id,
            "user_id": self.request.user.id,
            "comment_text": self.object.text,
            "created_at": self.object.created_at.isoformat(),
        }
        try:
            producer.send_message(topic, json.dumps(message))
        except Exception as e:
            print(f"Error sending message to Kafka: {e}")

        return response

    def get_success_url(self):
        return reverse_lazy("comment_list")


def get_user_data_from_token(token):
    """
    Извлекает данные пользователя из JWT-токена.

    :param token: Строка JWT-токена
    :return: Словарь с данными пользователя или пустой словарь при ошибке
    """
    jwt_auth = JWTAuthentication()
    try:
        validated_token = jwt_auth.get_validated_token(token)
        user_data = jwt_auth.get_user(validated_token)
        return {
            "id": user_data.id,
            "username": user_data.username,
            "email": user_data.email,
        }
    except AuthenticationFailed:
        return {}
