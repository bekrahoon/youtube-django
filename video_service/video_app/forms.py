from django import forms

from video_app.models import Video


class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = (
            "title",
            "description",
            "category",
            "preview",
            "file",
            "duration",
        )


class VideoFilterForm(forms.Form):
    query = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(attrs={"placeholder": "Введите ключевое слово"}),
    )
    category = forms.CharField(
        required=False,
        label="Категория",
        widget=forms.TextInput(attrs={"placeholder": "Введите категорию"}),
    )
