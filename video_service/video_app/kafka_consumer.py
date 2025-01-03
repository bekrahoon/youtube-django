from confluent_kafka import Consumer, KafkaException, KafkaError
import json


def get_comment_data(video_id):
    """
    Получает данные о видео через Kafka consumer.
    """
    consumer_conf = {
        "bootstrap.servers": "kafka:9092",  # Адрес Kafka-брокера
        "group.id": "comment_group",
        "auto.offset.reset": "earliest",  # Или 'latest' в зависимости от требований
        "enable.auto.commit": True,
        "session.timeout.ms": 6000,  # Время ожидания для подтверждения активности потребителя
        "max.poll.interval.ms": 300000,  # Максимальное время между вызовами poll
    }
    consumer = Consumer(consumer_conf)
    topic = "comment-topic"

    try:
        consumer.subscribe([topic])

        while True:
            msg = consumer.poll(1.0)  # Ждем 1 секунду сообщений

            if msg is None:
                continue  # Если нет сообщений, пропускаем итерацию

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Достигли конца раздела, игнорируем
                    continue
                else:
                    raise KafkaException(msg.error())

            # Обрабатываем сообщение
            video_data = json.loads(msg.value().decode("utf-8"))
            if video_data["video_id"] == video_id:
                return video_data
    finally:
        consumer.close()

    return {}
