import logging
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import time
import elasticapm
from elasticapm import Client

# Настройка клиента ElasticAPM
client = Client(
    service_name="comment_service",  # Имя вашего сервиса
    server_url="http://192.168.1.33:8200",  # URL вашего APM-сервера
    timeout=10,
)
# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
        "auto.offset.reset": "earliest",  # Или 'latest' в зависимости от требований
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
                logger.warning(
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

            # Получаем строку из Kafka-сообщения (если это байты, то декодируем в строку)
            video_data = msg.value().decode("utf-8")
            try:
                # Преобразуем строку в словарь (JSON)
                video_data = json.loads(video_data)
                logger.debug(f"Тип данных после json.loads: {type(video_data)}")
                logger.debug(f"Данные сообщения: {video_data}")
                # Проверка, что video_data действительно является строкой JSON
                if isinstance(video_data, str):
                    video_data = json.loads(video_data)
                    logger.debug(
                        f"Тип данных после второго json.loads: {type(video_data)}"
                    )
                    logger.debug(
                        f"Данные сообщения после второго декодирования: {video_data}"
                    )
                # Проверяем, что данные являются словарем и содержат нужный ID
                if isinstance(video_data, dict):
                    if video_data.get("video_id") == video_id:
                        logger.info(f"Данные о видео с video_id {video_id} найдены.")
                        return video_data
                    else:
                        logger.info(
                            f"Данные о видео с video_id {video_id} не соответствуют."
                        )
                else:
                    # Если данные не являются словарем, логируем это
                    logger.warning(
                        f"Полученные данные не являются словарем: {video_data} (Тип данных: {type(video_data)})"
                    )
            except json.JSONDecodeError:
                # Логируем ошибку при парсинге JSON
                logger.error(
                    f"Ошибка при парсинге JSON из сообщения Kafka: {video_data}"
                )
                client.capture_exception()  # Отправка исключения в APM
            except Exception as e:
                # Логируем другие ошибки
                logger.exception(f"Неожиданная ошибка: {e}")
                client.capture_exception()  # Отправка исключения в APM

    except KafkaException as e:
        logger.error(f"Ошибка Kafka: {e}")
        client.capture_exception()  # Отправка исключения в APM
    finally:
        consumer.close()

    logger.warning(f"Данные о видео с video_id {video_id} не найдены.")
    return {}
