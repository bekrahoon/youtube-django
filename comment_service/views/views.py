import json
from django.urls import reverse
from django.views.generic import ListView, CreateView
from comment_app.models import Comment
from comment_app.forms import CommentForm
from comment_app.kafka_producer import KafkaProducer
from comment_app.kafka_consumer import get_video_data
from django.contrib.auth.mixins import LoginRequiredMixin


class CommentViewList(ListView):
    model = Comment
    template_name = "comment_app/comment_list.html"
    context_object_name = "comments"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_with_details = []

        for comment in context["comments"]:  # Используем загруженные комментарии
            # Получение данных о пользователе
            user_data = {
                "id": comment.user.id,
                "username": comment.user.username,
                "email": comment.user.email,
            }

            # Получение данных о видео через Kafka
            video_data = get_video_data(comment.video_id) or {}

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


class CommentPostView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment_app/comment_post.html"

    def form_valid(self, form):
        # Устанавливаем текущего пользователя как автора комментария
        form.instance.user = self.request.user
        # form.instance.video_id = self.kwargs.get("video_id")
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
        return reverse("comment_list")
