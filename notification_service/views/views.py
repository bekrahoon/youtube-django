import logging
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from notification_app.models import Notification
from .views_get_user_api import get_user_data_from_auth_service

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class NotificationsView(View):
    def get(self, request):
        user_data = get_user_data_from_auth_service(
            request.headers.get("Authorization")
        )
        if not user_data:
            logger.warning("Неверные данные пользователя. Возвращаем ошибку 403.")
            return JsonResponse({"error": "Неверные данные пользователя."}, status=403)

        # Получаем все уведомления текущего пользователя
        notifications = Notification.objects.filter(user_id=int(user_data["id"]))
        logger.info(f"Найдено уведомлений: {notifications.count()}")

        # Отображаем уведомления на странице
        return render(
            request,
            "notifications.html",
            {
                "notifications": notifications,
                "user_data": {
                    **user_data,  # Разворачиваем существующие данные
                    "id": int(user_data["id"]),  # Преобразуем id в int
                },
            },
        )


class MarkAsReadView(View):
    def get(self, request, id):
        user_data = get_user_data_from_auth_service(
            self.request.headers.get("Authorization")
        )
        if not user_data:
            logger.warning("Данные пользователя не найдены. Возвращаем ошибку 401.")
            return JsonResponse({"error": "User not found"}, status=401)

        # Находим уведомление по ID
        notification = get_object_or_404(Notification, id=id, user_id=user_data["id"])

        # Обновляем статус уведомления на 'read'
        notification.status = "read"
        notification.save()
        logger.info(f"Уведомление с ID {id} обновлено на 'read'.")

        # Перенаправляем обратно на страницу уведомлений
        return redirect("notifications")
