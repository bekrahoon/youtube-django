from django.apps import AppConfig
from .tasks import start_kafka_consumer


class NotificationAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notification_app"

    def ready(self):
        start_kafka_consumer.apply_async()
