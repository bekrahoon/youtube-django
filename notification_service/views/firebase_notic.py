# from django.db.models.signals import post_save
# from django.db import IntegrityError
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from notification_app.models import DeviceToken
from .views_get_user_api import get_user_data_from_auth_service_v2
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


import logging


class SaveFcmTokenView(APIView):
    permission_classes = [AllowAny]  # Отключаем стандартную проверку аутентификации

    def post(self, request):
        # Получение куки из заголовка
        cookie_header = request.headers.get("Cookie")
        if not cookie_header:
            logger.error("Cookie заголовок отсутствует.")
            return Response(
                {"status": "error", "message": "Cookie header is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Извлечение access_token из куки
        token_parts = [part.strip() for part in cookie_header.split(";")]
        access_token = next(
            (
                part.split("=")[1]
                for part in token_parts
                if part.startswith("access_token=")
            ),
            None,
        )

        if not access_token:
            logger.error("Access token отсутствует в куки.")
            return Response(
                {"status": "error", "message": "Access token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(f"Токен, полученный из куки: {access_token}")

        # Получение данных пользователя через внешний сервис
        user_data = get_user_data_from_auth_service_v2(access_token)
        if not user_data:
            logger.warning("Не удалось получить данные пользователя для токена.")
            return Response(
                {"status": "error", "message": "Invalid user data"},
                status=status.HTTP_403_FORBIDDEN,
            )

        logger.info(f"Получены данные пользователя: {user_data}")

        # Извлечение user_id из данных
        try:
            user_id = int(user_data["id"])
        except (KeyError, ValueError):
            logger.error("ID пользователя отсутствует или некорректен.")
            return Response(
                {"status": "error", "message": "User ID is missing or invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Получение токена устройства из тела запроса
        token = request.data.get("fcm_token")
        if not token:
            logger.error("FCM токен не предоставлен.")
            return Response(
                {"status": "error", "message": "FCM token not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверяем или создаем запись для этого пользователя
        device_token, created = DeviceToken.objects.get_or_create(user_id=user_id)
        device_token.fcm_token = token
        device_token.save()

        message = "Token created" if created else "Token updated"
        logger.info(f"FCM токен успешно сохранен для пользователя {user_id}.")
        return Response(
            {"status": "success", "message": message},
            status=status.HTTP_200_OK,
        )


def showFirebaseJS(request):
    data = (
        'importScripts("https://www.gstatic.com/firebasejs/8.6.3/firebase-app.js");'
        'importScripts("https://www.gstatic.com/firebasejs/8.6.3/firebase-messaging.js"); '
        "const firebaseConfig = {"
        '    apiKey: "AIzaSyDVw6VqCgcl2wP6VQrVA3HjWs7BnzlzW_A",'  #! добавить сюда apiKey
        '    authDomain: "clon-1ecee.firebaseapp.com",'  #! добавить сюда authDomain
        '    projectId: "clon-1ecee",'  #! добавить сюда projectId
        '    storageBucket: "clon-1ecee.firebasestorage.app",'  #! добавить сюда storageBucket
        '    messagingSenderId: "708525337657",'  #! добавить сюда messagingSenderId
        '    appId: "1:708525337657:web:fb47f7e1861af56c4cb1e8",'  #! добавить сюда appId
        '    measurementId: "G-7MRKKQQG1X"'  #! добавить сюда measurementId
        "};"
        "firebase.initializeApp(firebaseConfig);"
        "const messaging = firebase.messaging();"
        "messaging.onBackgroundMessage(function (payload) {"
        '    console.log("Received background message: ", payload);'
        "    const data = payload.data;"
        '    const notificationTitle = data.title || "Новое уведомление";'
        "    const notificationOptions = {"
        '        body: data.body || "",'
        '        icon: data.icon || "static/images/3062634.png",'
        '        image: data.image || "static/images/3062634.png",'
        "        data: {"
        '            url: data.url || "/"'  # Извлечение URL из data
        "        }"
        "    };"
        "    self.registration.showNotification(notificationTitle, notificationOptions);"
        "});"
        'self.addEventListener("notificationclick", function(event) {'
        "    event.notification.close();"
        "    const url = event.notification.data.url;"
        "    event.waitUntil("
        '        clients.matchAll({ type: "window", includeUncontrolled: true }).then(windowClients => {'
        "            for (let client of windowClients) {"
        '                if (client.url === url && "focus" in client) {'
        "                    return client.focus();"
        "                }"
        "            }"
        "            if (clients.openWindow) {"
        "                return clients.openWindow(url);"
        "            }"
        "        })"
        "    );"
        "});"
    )

    return HttpResponse(data, content_type="text/javascript")
