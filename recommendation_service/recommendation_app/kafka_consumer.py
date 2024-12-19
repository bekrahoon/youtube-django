from confluent_kafka import Consumer
import json

# Настройка Kafka Consumer
consumer_config = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "recommendation_service",
    "auto.offset.reset": "earliest",
}
consumer = Consumer(consumer_config)


def consume_videos():
    consumer.subscribe(["video_topic"])
    while True:
        msg = consumer.poll(1.0)  # Ждём сообщения
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        video_data = json.loads(msg.value().decode("utf-8"))
        process_video_data(video_data)


def process_video_data(video_data):
    # Логика обработки видео для рекомендаций
    print(f"Processing video: {video_data}")
    # Например, добавить видео в локальную базу данных рекомендаций
    ...
