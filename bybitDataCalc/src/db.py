# src/db.py
import logging
from datetime import datetime
from typing import Any, List, Dict

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection
from sqlalchemy import text

async def get_symbols(engine: AsyncEngine) -> List[str]:
    logging.debug("Fetching unique symbols from database")
    async with engine.connect() as conn:
        try:
            result = await conn.execute(text("SELECT DISTINCT symbol FROM bybitmarketdata"))
            symbols = [row[0] for row in result.fetchall()]
            logging.debug(f"Found {len(symbols)} symbols")
            return symbols
        except Exception as e:
            logging.error(f"Error fetching symbols: {e}")
            return []

async def fetch_data_for_symbol(conn: AsyncConnection, symbol: str, max_period: int) -> List[Any]:
    logging.debug(f"Fetching data for symbol: {symbol}")
    query = text("""
        SELECT timestamp_unix_utc, open, high, low, close, volume
        FROM bybitmarketdata
        WHERE symbol = :symbol
        ORDER BY timestamp_unix_utc DESC
        LIMIT :limit
    """)
    try:
        result = await conn.execute(query, {'symbol': symbol, 'limit': max_period})
        data = result.fetchall()
        logging.debug(f"Records fetched for {symbol}: {len(data)}")
        return data
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return []

async def create_table_if_not_exists(engine: AsyncEngine) -> None:
    logging.debug("Ensuring table bybit_signals_metrics exists")
    ddl = """
    CREATE TABLE IF NOT EXISTS bybit_signals_metrics (
        symbol varchar(255) NOT NULL,
        hour_utc timestamp NOT NULL,
        calculation_time timestamp NOT NULL,
        atr_14 numeric,
        ema_14 numeric,
        ema_200 numeric,
        bollinger_upper numeric,
        bollinger_middle numeric,
        bollinger_lower numeric,
        ha_open numeric,
        ha_high numeric,
        ha_low numeric,
        ha_close numeric,
        lr_slope_angle numeric,
        rsi numeric,
        macd numeric,
        macd_signal numeric,
        macd_hist numeric,
        stoch_k numeric,
        stoch_d numeric,
        adx numeric,
        cci numeric,
        ichimoku_tenkan numeric,
        ichimoku_kijun numeric,
        obv numeric,
        CONSTRAINT unique_symbol_hour PRIMARY KEY (symbol, hour_utc)
    );
    """
    async with engine.begin() as conn:
        try:
            await conn.execute(text(ddl))
            logging.debug("Table signals_metrics ensured")
        except Exception as e:
            logging.error(f"Error creating table: {e}")

async def check_db_record(conn: AsyncConnection, symbol: str, hour_utc: datetime) -> Any:
    query = text("""
        SELECT symbol, hour_utc, calculation_time,
               atr_14, ema_14, ema_200,
               bollinger_upper, bollinger_middle, bollinger_lower,
               ha_open, ha_high, ha_low, ha_close,
               lr_slope_angle, rsi, macd, macd_signal, macd_hist, 
               stoch_k, stoch_d, adx, cci,
               ichimoku_tenkan, ichimoku_kijun,
               obv
        FROM bybit_signals_metrics
        WHERE symbol = :symbol AND hour_utc = :hour_utc
    """)
    result = await conn.execute(query, {'symbol': symbol, 'hour_utc': hour_utc})
    return result.fetchone()

async def save_to_db(engine: AsyncEngine, result: Dict[str, Any]) -> None:
    logging.debug(f"Saving result for {result['symbol']} to database")
    insert_query = """
    INSERT INTO bybit_signals_metrics (
        symbol, hour_utc, calculation_time,
        atr_14, ema_14, ema_200,
        bollinger_upper, bollinger_middle, bollinger_lower,
        ha_open, ha_high, ha_low, ha_close,
        lr_slope_angle, rsi, macd, macd_signal, macd_hist,
        stoch_k, stoch_d, adx, cci,
        ichimoku_tenkan, ichimoku_kijun,
        obv
    ) VALUES (
        :symbol, :hour_utc, :calculation_time,
        :atr_14, :ema_14, :ema_200,
        :bollinger_upper, :bollinger_middle, :bollinger_lower,
        :ha_open, :ha_high, :ha_low, :ha_close,
        :lr_slope_angle, :rsi, :macd, :macd_signal, :macd_hist,
        :stoch_k, :stoch_d, :adx, :cci,
        :ichimoku_tenkan, :ichimoku_kijun,
        :obv
    ) ON CONFLICT (symbol, hour_utc) DO UPDATE SET
        calculation_time = EXCLUDED.calculation_time,
        atr_14 = EXCLUDED.atr_14,
        ema_14 = EXCLUDED.ema_14,
        ema_200 = EXCLUDED.ema_200,
        bollinger_upper = EXCLUDED.bollinger_upper,
        bollinger_middle = EXCLUDED.bollinger_middle,
        bollinger_lower = EXCLUDED.bollinger_lower,
        ha_open = EXCLUDED.ha_open,
        ha_high = EXCLUDED.ha_high,
        ha_low = EXCLUDED.ha_low,
        ha_close = EXCLUDED.ha_close,
        lr_slope_angle = EXCLUDED.lr_slope_angle,
        rsi = EXCLUDED.rsi,
        macd = EXCLUDED.macd,
        macd_signal = EXCLUDED.macd_signal,
        macd_hist = EXCLUDED.macd_hist,
        stoch_k = EXCLUDED.stoch_k,
        stoch_d = EXCLUDED.stoch_d,
        adx = EXCLUDED.adx,
        cci = EXCLUDED.cci,
        ichimoku_tenkan = EXCLUDED.ichimoku_tenkan,
        ichimoku_kijun = EXCLUDED.ichimoku_kijun,
        obv = EXCLUDED.obv
    """
    try:
        values = {
            "symbol": result['symbol'],
            "hour_utc": datetime.fromisoformat(result['hour_utc']),
            "calculation_time": datetime.fromisoformat(result['calculation_time']),
            "atr_14": result['metrics']['ATR_14'],
            "ema_14": result['metrics']['EMA_14'],
            "ema_200": result['metrics']['EMA_200'],
            "bollinger_upper": result['metrics']['Bollinger_upper'],
            "bollinger_middle": result['metrics']['Bollinger_middle'],
            "bollinger_lower": result['metrics']['Bollinger_lower'],
            "ha_open": result['metrics']['Heiken_Ashi_open'],
            "ha_high": result['metrics']['Heiken_Ashi_high'],
            "ha_low": result['metrics']['Heiken_Ashi_low'],
            "ha_close": result['metrics']['Heiken_Ashi_close'],
            "lr_slope_angle": result['metrics']['Linear_Regression_slope_angle'],
            "rsi": result['metrics']['RSI'],
            "macd": result['metrics']['MACD'],
            "macd_signal": result['metrics']['MACD_signal'],
            "macd_hist": result['metrics']['MACD_hist'],
            "stoch_k": result['metrics']['Stochastic_k'],
            "stoch_d": result['metrics']['Stochastic_d'],
            "adx": result['metrics']['ADX'],
            "cci": result['metrics']['CCI'],
            "ichimoku_tenkan": result['metrics']['Ichimoku_tenkan'],
            "ichimoku_kijun": result['metrics']['Ichimoku_kijun'],
            "obv": result['metrics']['OBV']
        }
        async with engine.begin() as conn:
            await conn.execute(text(insert_query), values)
            logging.debug(f"Data for {result['symbol']} saved. Verifying record...")
            record = await check_db_record(conn, result['symbol'], values['hour_utc'])
            if record:
                logging.debug(f"Record found: {record}")
            else:
                logging.error(f"Record for {result['symbol']} not found after insert.")
    except Exception as e:
        logging.error(f"Error saving {result['symbol']}: {e}")
