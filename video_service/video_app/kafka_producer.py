import json
from confluent_kafka import Producer

# Настройки Kafka
KAFKA_CONFIG = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "video-topic",
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
            key=str(key).encode("utf-8"),
            value=json.dumps(value).encode("utf-8"),
            callback=lambda err, msg: (
                print(f"Сообщение доставлено: {msg.topic()} [{msg.partition()}]")
                if not err
                else print(f"Ошибка: {err}")
            ),
        )
        producer.flush()  # Ждем завершения отправки
        print(f"Событие отправлено: {key} -> {value}")
    except Exception as e:
        print(f"Ошибка отправки события в Kafka: {str(e)}")
