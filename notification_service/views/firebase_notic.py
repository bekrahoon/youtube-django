from django.db.models.signals import post_save
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.dispatch import receiver
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from chat.models import MyUser, Message
from google.oauth2 import service_account
from decouple import config
import google.auth.transport.requests
import requests
from typing import Any


class SaveFcmTokenView(APIView):
    permission_classes = [IsAuthenticated]  # Проверка на авторизацию

    def post(self, request: HttpRequest) -> Response:
        token: str = request.data.get("fcm_token")
        print(f"Received token: {token}")  # Логирование для отладки

        if not token:
            return Response(
                {"status": "error", "message": "Token not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(MyUser, id=request.user.id)
        user.fcm_token = token
        user.save()
        print(f"Token saved for user: {user.username}")

        return Response({"status": "success"}, status=status.HTTP_200_OK)


# Путь к вашему файлу сервисного аккаунта
SERVICE_ACCOUNT_FILE: str = config("FIREBASE_SERVICE_ACCOUNT_KEY")

# Аутентификация с использованием сервисного аккаунта
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE
)
scoped_credentials = credentials.with_scopes(
    ["https://www.googleapis.com/auth/firebase.messaging"]
)
request = google.auth.transport.requests.Request()
scoped_credentials.refresh(request)

access_token: str = scoped_credentials.token  # Токен доступа


def send_notification(
    token: str, title: str, body: str, click_action_url: Optional[str] = None
) -> None:

    url: str = "https://fcm.googleapis.com/v1/projects/chat-1a046/messages:send"
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    message: Dict[str, Any] = {
        "token": token,
        "data": {
            "title": title,
            "body": body,
            "url": click_action_url or "https://your-default-url.com",
            "icon": "static/images/3062634.png",
            "image": "static/images/images_notis.avif",
        },
    }

    payload: Dict[str, Any] = {"message": message}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Notification sent successfully:", response.json())
    else:
        # Логируем ошибку и удаляем невалидный токен
        print("Failed to send notification:", response.status_code, response.json())
        if response.status_code == 404:
            # Пример кода для удаления невалидного токена
            try:
                MyUser.objects.filter(fcm_token=token).update(fcm_token=None)
            except IntegrityError as e:
                print("Error updating token:", e)


@receiver(post_save, sender=Message)
def notify_users(
    sender: type[Message], instance: Message, created: bool, **kwargs: Any
) -> None:
    if created:
        group = instance.group

        # Проверка, является ли группа публичной или личной
        if group.is_private:  # Предположим, что у группы есть флаг is_private
            users = group.members.all()  # Личные переписки
        else:
            users = group.participants.all()  # Публичные группы

        user_tokens = users.values_list(
            "fcm_token", flat=True
        )  # Преобразование QuerySet в список

        for token in set(user_tokens):
            if token:
                # Формирование URL с идентификатором группы
                message_url = f"http://127.0.0.1:8000/group/{group.id}/"

                if instance.body_decrypted:  # Проверяем, есть ли текстовое сообщение
                    message_content = f"╰┈➤ {instance.body_decrypted}"
                elif instance.file:  # Если есть файл, отображаем это
                    message_content = "📎 Вам отправлен Файл"
                send_notification(
                    token,
                    f"{instance.user.username} 📩 ",
                    message_content,
                    click_action_url=message_url,
                )


def showFirebaseJS(request):
    data = (
        'importScripts("https://www.gstatic.com/firebasejs/8.6.3/firebase-app.js");'
        'importScripts("https://www.gstatic.com/firebasejs/8.6.3/firebase-messaging.js"); '
        "const firebaseConfig = {"
        '    apiKey: "",'  #! добавить сюда apiKey
        '    authDomain: "",'  #! добавить сюда authDomain
        '    projectId: "",'  #! добавить сюда projectId
        '    storageBucket: "",'  #! добавить сюда storageBucket
        '    messagingSenderId: "",'  #! добавить сюда messagingSenderId
        '    appId: "",'  #! добавить сюда appId
        '    measurementId: ""'  #! добавить сюда measurementId
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
