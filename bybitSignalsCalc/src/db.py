import os
import json
import logging
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text
from src.config import DATABASE_URL, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, ECHO

def create_async_engine_for_db() -> AsyncEngine:
    return create_async_engine(
        DATABASE_URL,
        echo=ECHO,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT
    )

async def create_signals_table_if_not_exists(engine: AsyncEngine) -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS bybit_signals_results (
        symbol varchar(255) NOT NULL,
        signal varchar(10) NOT NULL,
        entry_price numeric NOT NULL,
        stop_loss numeric,
        target_profit numeric,
        risk numeric,
        timestamp timestamp NOT NULL,
        PRIMARY KEY (symbol, timestamp)
    );
    """
    async with engine.begin() as conn:
        await conn.execute(text(ddl))
        logging.info("Table bybit_signals_results ensured.")

async def save_signal_to_db(engine: AsyncEngine, signal: dict) -> None:
    insert_query = """
    INSERT INTO bybit_signals_results (
        symbol, signal, entry_price, stop_loss, target_profit, risk, timestamp
    ) VALUES (
        :symbol, :signal, :entry_price, :stop_loss, :target_profit, :risk, :timestamp
    ) ON CONFLICT (symbol, timestamp) DO UPDATE SET
        signal = EXCLUDED.signal,
        entry_price = EXCLUDED.entry_price,
        stop_loss = EXCLUDED.stop_loss,
        target_profit = EXCLUDED.target_profit,
        risk = EXCLUDED.risk
    """
    async with engine.begin() as conn:
        await conn.execute(text(insert_query), signal)
        logging.info(f"Signal for {signal['symbol']} saved/updated.")

async def get_calculated_metrics(engine: AsyncEngine) -> list:
    query = """
        SELECT symbol, hour_utc, calculation_time,
               atr_14, ema_14, ema_200,
               bollinger_upper, bollinger_middle, bollinger_lower,
               ha_open, ha_high, ha_low, ha_close,
               lr_slope_angle, rsi, macd, macd_signal, macd_hist,
               stoch_k, stoch_d, adx, cci,
               ichimoku_tenkan, ichimoku_kijun,
               obv
        FROM bybit_signals_metrics
        ORDER BY calculation_time DESC
    """
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        rows = result.fetchall()
    metrics_list = []
    for row in rows:
        r = dict(row._mapping)
        metrics = {
            "ATR_14": r["atr_14"],
            "EMA_14": r["ema_14"],
            "EMA_200": r["ema_200"],
            "Bollinger_upper": r["bollinger_upper"],
            "Bollinger_middle": r["bollinger_middle"],
            "Bollinger_lower": r["bollinger_lower"],
            "Heiken_Ashi_open": r["ha_open"],
            "Heiken_Ashi_high": r["ha_high"],
            "Heiken_Ashi_low": r["ha_low"],
            "Heiken_Ashi_close": r["ha_close"],
            "Linear_Regression_slope_angle": r["lr_slope_angle"],
            "RSI": r["rsi"],
            "MACD": r["macd"],
            "MACD_signal": r["macd_signal"],
            "MACD_hist": r["macd_hist"],
            "Stochastic_k": r["stoch_k"],
            "Stochastic_d": r["stoch_d"],
            "ADX": r["adx"],
            "CCI": r["cci"],
            "Ichimoku_tenkan": r["ichimoku_tenkan"],
            "Ichimoku_kijun": r["ichimoku_kijun"],
            "OBV": r["obv"]
        }
        metrics_list.append({
            "symbol": r["symbol"],
            "hour_utc": r["hour_utc"].isoformat() if isinstance(r["hour_utc"], datetime) else r["hour_utc"],
            "calculation_time": r["calculation_time"].isoformat() if isinstance(r["calculation_time"], datetime) else r["calculation_time"],
            "metrics": metrics
        })
    return metrics_list

async def run_main_logic() -> list:
    engine = create_async_engine_for_db()
    # Убедимся, что таблица для сигналов существует
    await create_signals_table_if_not_exists(engine)
    metrics_list = await get_calculated_metrics(engine)
    logging.info("Retrieved calculated metrics:")
    logging.info(json.dumps(metrics_list, indent=2, default=str))
    await engine.dispose()
    return metrics_list
