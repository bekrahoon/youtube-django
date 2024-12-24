import json
import logging
from confluent_kafka import Producer

# Настройки Kafka
KAFKA_CONFIG = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "comment-topic",
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_kafka_producer():
    """Создает и возвращает Kafka Producer."""
    logger.info("Создание Kafka Producer с настройками: %s", KAFKA_CONFIG)
    return Producer(KAFKA_CONFIG)


def send_event(topic, key, value):
    logger.info(
        "Отправка в Kafka - Топик: %s, Ключ: %s, Значение: %s", topic, key, value
    )
    """
    Отправляет событие в Kafka.
    :param topic: Топик Kafka
    :param key: Ключ события
    :param value: Значение события
    """
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
        logger.error("Ошибка при отправке события в Kafka: %s", str(e))
