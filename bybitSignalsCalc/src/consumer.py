import os
import json
import logging
from kafka import KafkaConsumer
from src.scheduler import scheduler_job
from src.logger_config import setup_logger

setup_logger()

def start_kafka_consumer():
    """
    Консьюмер ожидает сообщение от bybitDataCalc в Kafka.
    После получения сообщения в топике, заданном переменной окружения
    KAFKA_METRICS_FINISHED_TOPIC (по умолчанию "bybit-data-calc-finished"),
    запускается расчёт сигналов.
    """
    kafka_broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    topic = os.getenv("KAFKA_METRICS_FINISHED_TOPIC", "bybit-data-calc-finished")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[kafka_broker],
        auto_offset_reset='latest',
        group_id='bybit-signals-calc-group'
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
