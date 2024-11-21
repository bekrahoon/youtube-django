from django import forms

from video_app.models import Video


class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = (
            "title",
            "description",
            "preview",
            "file",
            "duration",
        )
