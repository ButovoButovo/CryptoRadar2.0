import os
import json
import logging
import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine
from src.config import DATABASE_URL, MAX_PERIOD, semaphore, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, ECHO
from src.db import create_table_if_not_exists, get_symbols, fetch_data_for_symbol, save_to_db
from src.indicators import process_data
from src.producer import send_kafka_notification
from src.logger_config import setup_logger

setup_logger()

async def process_symbol(engine, symbol: str) -> dict:
    async with semaphore:
        try:
            async with engine.connect() as conn:
                data = await fetch_data_for_symbol(conn, symbol, max_period=MAX_PERIOD)
            result = process_data(data, symbol)
            if result:
                await save_to_db(engine, result)
            return result
        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")
            return None

async def run_main_logic():
    engine = create_async_engine(
        DATABASE_URL,
        echo=ECHO,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT
    )
    await create_table_if_not_exists(engine)
    symbols = await get_symbols(engine)
    if not symbols:
        logging.warning("No symbols found. Exiting.")
        return []
    results = await asyncio.gather(*(process_symbol(engine, symbol) for symbol in symbols))
    results = [res for res in results if res]
    logging.info("Calculation results:")
    logging.info(json.dumps(results, indent=2, default=str))
    await engine.dispose()
    return results

def scheduler_job():
    logging.info(f"Started processing job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        results = asyncio.run(run_main_logic())
        # После завершения расчетов отправляем уведомление в Kafka
        notification = {
            "status": "calc_finished",
            "timestamp": datetime.now().isoformat()
        }
        send_kafka_notification(notification)
    except Exception as e:
        logging.error(f"Processing error: {e}")
