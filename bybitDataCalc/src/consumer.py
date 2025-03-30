import os
import logging
from kafka import KafkaConsumer
from src.scheduler import scheduler_job
from src.logger_config import setup_logger

setup_logger()

def start_kafka_consumer():
    """
    Подписывается на топик, заданный переменной окружения KAFKA_DATA_FETCHED_TOPIC 
    (по умолчанию "bybit-data-fetched"), и при получении сообщения вызывает scheduler_job.
    """
    kafka_broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    topic = os.getenv("KAFKA_DATA_FETCHED_TOPIC", "bybit-data-fetched")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[kafka_broker],
        auto_offset_reset='latest',
        group_id='bybit-data-calc-group'
    )
    logging.info(f"Kafka consumer started. Waiting for messages on topic {topic}...")
    try:
        for message in consumer:
            msg = message.value.decode('utf-8')
            logging.info(f"Received Kafka message: {msg}")
            scheduler_job()
    except Exception as e:
        logging.error(f"Kafka consumer error: {e}")
    finally:
        consumer.close()
