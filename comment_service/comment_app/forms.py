from django.forms import ModelForm
from comment_app.models import Comment


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)
