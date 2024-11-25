import json
import mimetypes
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from video_app.models import Video
from video_app.forms import VideoFilterForm, VideoForm
from video_app.tasks import proccess_video
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from video_app.kafka_producer import send_event  # Импортируем продюсер Kafka


class VideoListView(ListView):
    """Отображение списка всех видео с поиском и фильтрацией"""

    model = Video
    template_name = "video_app/video_list.html"
    context_object_name = "videos"

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query", "").strip()
        category = self.request.GET.get("category", "").strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(keywords__icontains=query)
            )
        if category:
            queryset = queryset.filter(category__icontains=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = VideoFilterForm(self.request.GET)
        return context


class VideoDetailView(DetailView):
    """Отображение видео"""

    model = Video
    template_name = "video_app/video_watch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        return context


class VideoCreateView(CreateView):
    """Создание нового видео"""

    model = Video
    form_class = VideoForm
    template_name = "video_app/video_form.html"

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Отправляем событие в Kafka после успешного создания видео
        event_data = {
            "user_id": self.request.user.id,
            "video_id": self.object.id,
            "title": self.object.title,
            "timestamp": self.object.created_at.isoformat(),
        }
        try:
            send_event(
                topic="video-topic",
                key=str(self.object.id),
                value=json.dumps(event_data),
            )
            print("Событие успешно отправлено в Kafka")
        except Exception as e:
            print(f"Ошибка при отправке события в Kafka: {str(e)}")

        return response

    def get_success_url(self):
        print("Перенаправление на страницу списка видео")
        return reverse("video_list")  # После создания перенаправляем на список видео


class VideoUpdateView(UpdateView):
    """Обновление видео"""

    model = Video
    template_name = "video_app/video_form.html"
    form_class = VideoForm
    permission_classes = [IsAuthenticated]

    def get_success_url(self):
        return reverse("video_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["video"] = self.object
        return context

    def dispatch(self, request, *args, **kwargs):
        video = self.get_object()
        if video.user != request.user:
            return JsonResponse(
                {"error": "You don't have permission to access this video"}, status=403
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Отправляем событие в Kafka после успешного создания видео
        event_data = {
            "user_id": self.request.user.id,
            "video_id": self.object.id,
            "title": self.object.title,
            "timestamp": self.object.created_at.isoformat(),
        }
        try:
            send_event(
                topic="video_uploads",
                key=str(self.object.id),
                value=json.dumps(event_data),
            )
            print("Событие успешно отправлено в Kafka")
        except Exception as e:
            print(f"Ошибка при отправке события в Kafka: {str(e)}")

        return response

    def get_success_url(self):
        print("Перенаправление на страницу списка видео")
        return reverse("video_list")  # После создания перенаправляем на список видео


class VideoDeleteView(DeleteView):
    """Удаление видео"""

    model = Video
    template_name = "video_app/video_confirm_delete.html"
    context_object_name = "video"

    def get_success_url(self):
        return reverse("video_list")  # После удаления перенаправляем на список видео

    def dispatch(self, request, *args, **kwargs):
        video = self.get_object()
        if video.user != request.user:
            return JsonResponse(
                {"error": "You don't have permission to access this video"}, status=403
            )
        return super().dispatch(request, *args, **kwargs)


class StreamVideoView(View):
    def get(self, request, pk):
        video = get_object_or_404(Video, id=pk)
        file_path = video.file.path
        mime_type, _ = mimetypes.guess_type(file_path)
        response = FileResponse(open(file_path, "rb"), content_type=mime_type)
        response["Content-Disposition"] = f"inline; filename={video.title}"
        return response


class TranscodeVideoView(View):
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            resolution = data.get("resolution")
            video = get_object_or_404(Video, id=pk)
            print(f"Video found: {video.title}")
            proccess_video.delay(video.id, resolution)
            print("Transcode started")
            return JsonResponse(
                {"status": "success", "message": "Transcoding started"}, status=200
            )
        except Exception as e:
            print(f"Error during transcoding: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class LiveStreamView(View):
    def get(self, request):
        return render(request, "video_app/live_stream.html")
