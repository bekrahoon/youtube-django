from confluent_kafka import Consumer, KafkaException, KafkaError
import json


def get_video_data(video_id):
    """
    Получает данные о видео через Kafka consumer.
    """
    consumer_conf = {
        "bootstrap.servers": "kafka:9092",  # Адрес Kafka-брокера
        "group.id": "video-service-group",
        "auto.offset.reset": "earliest",  # Или 'latest' в зависимости от требований
        "enable.auto.commit": True,
    }
    consumer = Consumer(consumer_conf)
    topic = "video-topic"

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
