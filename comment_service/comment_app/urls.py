from django.urls import path
from views.views import CommentPostView, CommentViewList


urlpatterns = [
    path("", CommentViewList.as_view(), name="comment_list"),
    path("post/", CommentPostView.as_view(), name="comment_post"),
]
