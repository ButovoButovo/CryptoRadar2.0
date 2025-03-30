import os
import json
import logging
import asyncio
from datetime import datetime
from src.db import run_main_logic, save_signal_to_db, create_signals_table_if_not_exists, create_async_engine_for_db
from src.strategy import generate_trade_signal
from src.producer import send_kafka_notification
from src.config import DATABASE_URL, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, ECHO

def scheduler_job():
    logging.info(f"Started processing job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        results = asyncio.run(run_main_logic())
        signals = []
        for res in results:
            signal = generate_trade_signal(res)
            if signal["signal"] != "NONE":
                signals.append(signal)
        if signals:
            topic = os.getenv("KAFKA_FINISHED_TOPIC", "bybit-signals-calc-finished")
            # Создаем новое соединение для сохранения сигналов
            engine = create_async_engine_for_db()
            for sig in signals:
                asyncio.run(save_signal_to_db(engine, sig))
                send_kafka_notification(topic, sig)
            asyncio.run(engine.dispose())
        else:
            logging.info("No valid trade signals generated.")
    except Exception as e:
        logging.error(f"Processing error: {e}")
