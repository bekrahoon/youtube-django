import json
import logging
from confluent_kafka import Producer
import elasticapm
from elasticapm import Client

# Настройки Kafka
KAFKA_CONFIG = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "comment-topic",
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка клиента ElasticAPM
client = Client(
    service_name="comment_service",  # Имя вашего сервиса
    server_url="http://192.168.1.33:8200",  # URL вашего APM-сервера
    timeout=10,
)


def get_kafka_producer():
    """Создает и возвращает Kafka Producer."""
    logger.info("Создание Kafka Producer с настройками: %s", KAFKA_CONFIG)
    return Producer(KAFKA_CONFIG)


def send_event(topic, key, value):
    """
    Отправляет событие в Kafka.
    :param topic: Топик Kafka
    :param key: Ключ события
    :param value: Значение события
    """
    logger.info(
        "Отправка в Kafka - Топик: %s, Ключ: %s, Значение: %s", topic, key, value
    )

    producer = get_kafka_producer()
    try:
        producer.produce(
            topic,
            key=str(key).encode("utf-8"),
            value=json.dumps(value).encode("utf-8"),
            callback=lambda err, msg: (
                logger.info(f"Сообщение доставлено: {msg.topic()} [{msg.partition()}]")
                if not err
                else logger.error(f"Ошибка при доставке сообщения: {err}")
            ),
        )
        producer.flush()  # Ждем завершения отправки
        logger.info("Событие успешно отправлено в Kafka: %s -> %s", key, value)

    except Exception as e:
        # Логируем ошибку
        logger.error("Ошибка при отправке события в Kafka: %s", str(e))
        # Отправляем исключение в APM
        client.capture_exception(event_type="error")  # Добавляем event_type
