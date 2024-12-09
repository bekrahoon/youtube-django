from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import time


def get_video_data(video_id, timeout=10):
    """
    Получает данные о видео через Kafka consumer.

    :param video_id: Идентификатор видео для поиска.
    :param timeout: Максимальное время ожидания в секундах.
    :return: Данные о видео или пустой словарь, если данные не были получены.
    """
    consumer_conf = {
        "bootstrap.servers": "kafka:9092",  # Адрес Kafka-брокера
        "group.id": "video_group",
        "auto.offset.reset": "latest",  # Или 'latest' в зависимости от требований
        "enable.auto.commit": True,
    }

    consumer = Consumer(consumer_conf)
    topic = "video-topic"
    consumer.subscribe([topic])

    start_time = time.time()

    try:
        while True:
            # Проверяем, не прошло ли заданное время ожидания
            if time.time() - start_time > timeout:
                print(
                    f"Время ожидания истекло. Не удалось получить данные о видео с video_id {video_id}."
                )
                break

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
            if video_data.get("video_id") == video_id:
                print(f"Данные о видео с video_id {video_id} найдены.")
                return video_data

    except KafkaException as e:
        print(f"Ошибка Kafka: {e}")
    finally:
        consumer.close()

    print(f"Данные о видео с video_id {video_id} не найдены.")
    return {}
