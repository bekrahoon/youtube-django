from confluent_kafka import Producer

# Настройки Kafka
KAFKA_CONFIG = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "comment-topic",
}


def get_kafka_producer():
    """Создает и возвращает Kafka Producer."""
    return Producer(KAFKA_CONFIG)


def send_event(topic, key, value):
    print(f"Отправка в Kafka - Топик: {topic}, Ключ: {key}, Значение: {value}")
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
        print(f"Событие отправлено: {key} -> {value}")
    except Exception as e:
        print(f"Ошибка отправки события в Kafka: {str(e)}")
