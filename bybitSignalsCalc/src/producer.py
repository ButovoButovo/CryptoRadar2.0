import os
import json
import logging
from kafka import KafkaProducer

def send_kafka_notification(topic: str, message: dict):
    kafka_broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    producer = KafkaProducer(
        bootstrap_servers=[kafka_broker],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(topic, message)
    producer.flush()
    producer.close()
    logging.info(f"Sent Kafka notification to topic {topic}: {message}")
