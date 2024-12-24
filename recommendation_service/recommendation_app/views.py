from django.db import connections


def fetch_videos():
    with connections["default"].cursor() as cursor:
        cursor.execute(
            "SELECT video_id, title, description, tags, category FROM video_video"
        )
        rows = cursor.fetchall()
    return rows


def generate_recommendations(user_id):
    videos = fetch_videos()
    # Реализация логики рекомендаций на основе данных
