from confluent_kafka import Producer
import logging

# Настройки Kafka
KAFKA_CONFIG = {
    "bootstrap.servers": "kafka:9092",  # Укажите адрес вашего Kafka-брокера
    "client.id": "comment-topic",
}


def get_kafka_producer():
    """Создает и возвращает Kafka Producer."""
    return Producer(KAFKA_CONFIG)


def send_event(topic, key, value):
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
            key=key,
            value=value,
        )
        producer.flush()  # Ждем завершения отправки
        logging.info(f"Событие отправлено: {key} -> {value}")
    except Exception as e:
        logging.error(f"Ошибка отправки события в Kafka: {str(e)}")
