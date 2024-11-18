from django.shortcuts import render, redirect
from django.views import View
from auth_app.forms import CustomRegisterForm, CustomLoginForm
from django.contrib import messages
from django.contrib.auth import login


class RegisterView(View):
    def get(self, request):
        form = CustomRegisterForm()
        return render(request, "auth_app/register.html", {"form": form})

    def post(self, request):
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful, please log in")
            return redirect("login")
        return render(request, "auth_app/register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()
        return render(request, "auth_app/login.html", {"form": form})

    def post(self, request):
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("user-detail")
        messages.error(request, "Login failed, please try again")
        return render(request, "auth_app/login.html", {"form": form})
