from django.http import JsonResponse
from rest_framework.authentication import get_authorization_header
import requests


def jwt_auth_middleware(get_response):
    def middleware(request):
        auth = get_authorization_header(request).split()
        if auth and auth[0].lower() == b"bearer":
            token = auth[1].decode("utf-8")
            response = requests.post(
                "http://auth_service:8000/auth/verify_token/", data={"token": token}
            )
            if response.status_code != 200:
                return JsonResponse({"error": "Invalid token"}, status=401)
        return get_response(request)

    return middleware
