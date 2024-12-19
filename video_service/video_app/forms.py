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
            "tags",
            "duration",
        )

    def save(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Извлекаем пользователя, если он передан
        instance = super().save(*args, **kwargs)
        if user:
            instance.user = user  # Устанавливаем пользователя на объект
            instance.save()  # Сохраняем объект с пользователем
        return instance


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
