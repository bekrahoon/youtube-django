from django.urls import path
from views.views import CommentListAndPostView

urlpatterns = [
    path("", CommentListAndPostView.as_view(), name="comment_list_and_post"),
]
