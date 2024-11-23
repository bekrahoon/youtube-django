from urllib import response
from django.urls import reverse_lazy
from comment_app.models import Comment
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from comment_app.forms import CommentForm


class CommentViewList(ListView):
    model = Comment
    template_name = "comment_app/comment_list.html"
    context_object_name = "comments"
    queryset = Comment.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = "Список комментариев"
        return context


class CommentPostView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment_app/comment_post.html"
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def form_valid(self, request, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        return response

    def get_success_url(self):
        return reverse_lazy("comment_list")
