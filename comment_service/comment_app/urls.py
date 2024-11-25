from django.urls import path
from views.views import CommentPostView, CommentViewList


urlpatterns = [
    path("", CommentViewList.as_view(), name="comment-list"),
    path("post/", CommentPostView.as_view(), name="comment-post"),
]
