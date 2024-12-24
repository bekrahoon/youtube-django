from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = ""  # Убираем help_text
        self.fields["password2"].help_text = ""  # Убираем help_text
        self.fields["username"].help_text = ""  # Убираем help_text
        for field in self.fields.values():
            field.error_messages = {"required": ""}


class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "password")
