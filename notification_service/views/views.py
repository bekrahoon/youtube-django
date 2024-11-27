from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from notification_app.models import Notification


class NotificationsView(View):
    def get(self, request):
        # Получаем все уведомления текущего пользователя
        notifications = Notification.objects.filter(user=request.user)

        # Отображаем уведомления на странице
        return render(request, "notifications.html", {"notifications": notifications})


class MarkAsReadView(View):
    def get(self, request, id):
        # Находим уведомление по ID
        notification = get_object_or_404(Notification, id=id, user=request.user)

        # Обновляем статус уведомления на 'read'
        notification.status = "read"
        notification.save()

        # Перенаправляем обратно на страницу уведомлений
        return redirect("notifications")
