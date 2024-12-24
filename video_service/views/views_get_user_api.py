import requests
from requests.cookies import RequestsCookieJar


def get_user_data_from_auth_service(cookie_jar):
    url = "http://192.168.1.10:8000/api/user-info/"

    # Если cookie_jar - это строка (токен), создаем RequestsCookieJar
    if isinstance(cookie_jar, str):
        print("cookie_jar - строка, преобразуем в RequestsCookieJar")
        # Устанавливаем токен вручную
        token = cookie_jar
        cookie_jar = RequestsCookieJar()
        cookie_jar.set("access_token", token)

    # Проверяем, является ли cookie_jar объектом RequestsCookieJar
    if not isinstance(cookie_jar, RequestsCookieJar):
        print("Ошибка: cookie_jar не является объектом RequestsCookieJar.")
        return None

    # Печатаем cookies для отладки
    print(f"Cookies в cookie_jar: {cookie_jar}")

    # Извлекаем токен из cookies
    token = cookie_jar.get("access_token")  # Получаем токен напрямую через get()

    if not token:
        print("Токен не найден в cookies.")
        return None

    # Формируем заголовок Authorization с Bearer токеном
    # Токен уже в формате Bearer, не добавляем "Bearer" дважды
    headers = {"Authorization": token}  # Просто передаем сам токен

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Если статус ошибки, выбросит исключение
        return response.json()  # Если статус 200, возвращаем данные
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP при запросе: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с auth_service: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
    return None
