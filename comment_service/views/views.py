from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from comment_app.kafka_consumer import get_video_data
from comment_app.kafka_producer import send_event
from comment_app.forms import CommentForm
from comment_app.models import Comment
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import json


class CommentListAndPostView(View):
    template_name = "comment_app/comment_list_and_post.html"
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        # Получаем список комментариев
        comments = Comment.objects.filter(
            parent__isnull=True
        )  # Только корневые комментарии
        comments_with_details = []

        for comment in comments:
            # Используем кэширование для данных видео
            video_data = self.get_video_data_cached(comment.video_id)

            comments_with_details.append(
                {
                    "comment": comment,
                    "video": video_data,
                    "replies": comment.replies.all(),  # Получаем ответы на комментарий
                }
            )

        # Рендерим шаблон с комментариями и формой
        context = {
            "comments_with_details": comments_with_details,
            "comment_form": CommentForm(),
            "comment_list_title": "Список комментариев",
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Обрабатываем создание нового комментария
        form = CommentForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user
            form.instance.video_id = request.POST.get("video_id")  # Указываем video_id

            # Проверяем, является ли комментарий ответом
            parent_id = request.POST.get("parent_id")
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                form.instance.parent = parent_comment

            # Сохраняем комментарий
            new_comment = form.save()

            # Получаем данные о видео с кэшированием
            video_data = self.get_video_data_cached(new_comment.video_id)

            # Если video_data не получены, можно решить, как поступить:
            if not video_data:
                print(f"Данные о видео для video_id {new_comment.video_id} не найдены.")

            # Отправляем событие в Kafka после успешного создания комментария
            event_data = {
                "user_id": request.user.id,
                "text": new_comment.text,
                "timestamp": new_comment.created_at.isoformat(),
                "video_data": video_data,  # Добавляем данные о видео, если они есть
            }

            try:
                send_event(
                    topic=["comment-topic", "notification-topic"],
                    key=str(new_comment.id),
                    value=json.dumps(event_data),
                )

            except Exception as e:
                print(f"Ошибка при отправке события в Kafka: {str(e)}")

            # Возвращаем успешный ответ
            return JsonResponse(
                {"success": True, "message": "Комментарий добавлен!"}, status=200
            )

        else:
            print(f"Ошибка при валидации формы: {form.errors}")
        print(f"Ошибка при добавлении комментария: {form.errors}")
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    def get_video_data_cached(self, video_id):
        # Проверка наличия кэшированных данных о видео
        cached_data = cache.get(f"video_data_{video_id}")
        if cached_data is None:
            try:
                cached_data = get_video_data(video_id) or {}
                cache.set(
                    f"video_data_{video_id}", cached_data, timeout=3600
                )  # Кэшируем на 1 час
                print(f"Данные о видео для video_id {video_id} получены и кэшированы.")
            except Exception as e:
                print(
                    f"Ошибка при получении данных о видео для video_id {video_id}: {e}"
                )
                cached_data = {}
        else:
            print(f"Данные о видео для video_id {video_id} загружены из кэша.")
        return cached_data
