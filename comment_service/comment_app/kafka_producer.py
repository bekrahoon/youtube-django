from confluent_kafka import Producer


class KafkaProducer:
    def __init__(self, bootstrap_servers="kafka:9092"):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def send_message(self, topic, message):
        try:
            self.producer.produce(topic, message.encode("utf-8"))
            self.producer.flush()
        except Exception as e:
            print(f"Error sending message to kafka {e}")
