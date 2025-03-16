# main.py
import asyncio
import json
import logging

from sqlalchemy.ext.asyncio import create_async_engine
from src.logger_config import setup_logger
from src.config import DATABASE_URL, MAX_PERIOD, semaphore, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, ECHO
from src.db import create_table_if_not_exists, get_symbols, fetch_data_for_symbol, save_to_db
from src.indicators import process_data

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

async def main():
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
        return

    results = await asyncio.gather(*(process_symbol(engine, symbol) for symbol in symbols))
    results = [res for res in results if res]
    logging.info("Calculation results:")
    logging.info(json.dumps(results, indent=2, default=str))
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as main_e:
        logging.error(f"Fatal error in main process: {main_e}")
