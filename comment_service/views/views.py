from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from comment_app.kafka_consumer import get_video_data
from comment_app.kafka_producer import send_event
from comment_app.forms import CommentForm
from comment_app.models import Comment
import json

from .views_get_user_api import get_user_data_from_auth_service


class CommentListAndPostView(View):
    template_name = "comment_app/comment_list_and_post.html"

    def get(self, request, *args, **kwargs):
        user_data = get_user_data_from_auth_service(
            self.request.headers.get("Authorization")
        )
        if not user_data:
            return JsonResponse({"error": "User not found"}, status=401)

        comments = Comment.objects.filter(parent__isnull=True)
        comments_with_details = []

        for comment in comments:
            video_data = self.get_video_data_cached(comment.video_id)

            comments_with_details.append(
                {
                    "comment": comment,
                    "video": video_data,
                    "replies": comment.replies.all(),
                    "user": user_data,
                }
            )

        context = {
            "comments_with_details": comments_with_details,
            "comment_form": CommentForm(),
            "comment_list_title": "Список комментариев",
            "user_data": {
                **user_data,  # Разворачиваем существующие данные
                "id": int(user_data["id"]),  # Преобразуем id в int
            },
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_data = get_user_data_from_auth_service(
            self.request.headers.get("Authorization")
        )
        if not user_data:
            return JsonResponse({"error": "User not found"}, status=401)

        form = CommentForm(request.POST)

        if form.is_valid():
            form.instance.user_id = user_data["id"]
            form.instance.video_id = request.POST.get("video_id")

            parent_id = request.POST.get("parent_id")
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                form.instance.parent = parent_comment

            new_comment = form.save()

            video_data = self.get_video_data_cached(new_comment.video_id)

            if not video_data:
                print(f"Данные о видео для video_id {new_comment.video_id} не найдены.")

            event_data = {
                "user_id": user_data["id"],
                "text": new_comment.text,
                "timestamp": new_comment.created_at.isoformat(),
                "video_data": video_data,
            }

            try:
                for topic in ["comment-topic", "notification-topic"]:
                    send_event(
                        topic=topic,
                        key=str(new_comment.id),
                        value=json.dumps(event_data),
                    )

            except Exception as e:
                print(f"Ошибка при отправке события в Kafka: {str(e)}")

            return JsonResponse({"success": True})
        else:
            print(f"Ошибка при добавлении комментария: {form.errors}")
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    def put(self, request, *args, **kwargs):
        user_data = get_user_data_from_auth_service(
            self.request.headers.get("Authorization")
        )
        if not user_data:
            return JsonResponse({"error": "User not found"}, status=401)

        try:
            data = json.loads(request.body)
            comment_id = data.get("comment_id")
            new_text = data.get("text")

            if not comment_id or not new_text:
                return JsonResponse({"error": "Invalid data"}, status=400)

            comment = get_object_or_404(Comment, id=comment_id, user_id=user_data["id"])

            comment.text = new_text
            comment.save()

            return JsonResponse({"success": True, "updated_text": new_text})
        except Exception as e:
            print(f"Ошибка при обновлении комментария: {str(e)}")
            return JsonResponse({"error": "Something went wrong"}, status=500)

    def delete(self, request, *args, **kwargs):
        user_data = get_user_data_from_auth_service(
            self.request.headers.get("Authorization")
        )
        if not user_data:
            return JsonResponse({"error": "User not found"}, status=401)

        try:
            data = json.loads(request.body)
            comment_id = data.get("comment_id")

            if not comment_id:
                return JsonResponse({"error": "Comment ID not provided"}, status=400)

            comment = get_object_or_404(Comment, id=comment_id, user_id=user_data["id"])
            comment.delete()

            return JsonResponse({"success": True, "message": "Comment deleted"})
        except Exception as e:
            print(f"Ошибка при удалении комментария: {str(e)}")
            return JsonResponse({"error": "Something went wrong"}, status=500)

    def get_video_data_cached(self, video_id):
        cached_data = cache.get(f"video_data_{video_id}")
        if cached_data is None:
            try:
                cached_data = get_video_data(video_id) or {}
                cache.set(f"video_data_{video_id}", cached_data, timeout=3600)
                print(f"Данные о видео для video_id {video_id} получены и кэшированы.")
            except Exception as e:
                print(
                    f"Ошибка при получении данных о видео для video_id {video_id}: {e}"
                )
                cached_data = {}
        else:
            print(f"Данные о видео для video_id {video_id} загружены из кэша.")
        return cached_data
