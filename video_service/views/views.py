from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from video_app.models import Video
from video_app.forms import VideoForm


class VideoListView(ListView):
    """Отображение списка всех видео"""

    model = Video
    template_name = "video_app/video_list.html"
    context_object_name = "videos"


class VideoCreateView(CreateView):
    """Создание нового видео"""

    model = Video
    form_class = VideoForm
    template_name = "video_app/video_form.html"

    def get_success_url(self):
        return reverse("video_list")  # После создания перенаправляем на список видео


class VideoUpdateView(UpdateView):
    """Обновление видео"""

    model = Video
    form_class = VideoForm
    template_name = "video_app/video_form.html"

    def get_success_url(self):
        return reverse("video_list")  # После обновления перенаправляем на список видео

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["video"] = self.object  # Передаем объект видео в контекст
        return context


class VideoDeleteView(DeleteView):
    """Удаление видео"""

    model = Video
    template_name = "video_app/video_confirm_delete.html"
    context_object_name = "video"

    def get_success_url(self):
        return reverse("video_list")  # После удаления перенаправляем на список видео
