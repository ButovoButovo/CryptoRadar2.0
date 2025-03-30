import os
import json
import logging
from kafka import KafkaProducer

def send_kafka_notification(notification_message: dict):
    """
    Отправляет сообщение в Kafka.
    Топик берется из переменной окружения KAFKA_FINISHED_TOPIC (по умолчанию "bybit-data-calc-finished").
    """
    kafka_broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    producer = KafkaProducer(
        bootstrap_servers=[kafka_broker],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    topic = os.getenv("KAFKA_DATA_CALC_FINISHED_TOPIC", "bybit-data-calc-finished")
    producer.send(topic, notification_message)
    producer.flush()
    producer.close()
    logging.info(f"Sent Kafka notification to topic {topic}: {notification_message}")
