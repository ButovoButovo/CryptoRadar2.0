# src/indicators.py
from datetime import datetime
import pandas as pd
import pandas_ta as ta

from .utils import (convert_decimal_to_float, convert_decimal_to_float_df,
                   calc_slope, heiken_ashi, safe_last_value, unwrap)
from .config import INDICATOR_PARAMS, MAX_PERIOD

def process_data(data: list, symbol: str) -> dict:
    if not data:
        raise ValueError(f"No data for {symbol}")

    # Преобразуем список строк и создаем DataFrame
    converted = convert_decimal_to_float(data)
    df = pd.DataFrame(converted, columns=['timestamp_unix_utc', 'open', 'high', 'low', 'close', 'volume'])
    df = convert_decimal_to_float_df(df)
    df['timestamp'] = pd.to_datetime(df['timestamp_unix_utc'], unit='ms')
    df = df.sort_values('timestamp').set_index('timestamp')

    # Ресемплирование к часовым интервалам
    expected_hours = pd.date_range(end=df.index.max(), periods=MAX_PERIOD, freq='h')
    df = df.reindex(expected_hours)
    if df.isnull().values.any():
        df.ffill(inplace=True)
        df.bfill(inplace=True)
    if len(df) < MAX_PERIOD:
        raise ValueError(f"Insufficient data for {symbol}. Required: {MAX_PERIOD}, got: {len(df)}")

    try:
        # Расчет индикаторов
        atr = unwrap(ta.atr(df['high'], df['low'], df['close'], length=INDICATOR_PARAMS["ATR_PERIOD"]))
        ema14 = unwrap(ta.ema(df['close'], length=INDICATOR_PARAMS["EMA14_PERIOD"]))
        ema200 = unwrap(ta.ema(df['close'], length=INDICATOR_PARAMS["EMA200_PERIOD"]))
        bb = unwrap(ta.bbands(df['close'], length=INDICATOR_PARAMS["BB_PERIOD"]))
        ha_df = heiken_ashi(df)
        rsi = unwrap(ta.rsi(df['close'], length=INDICATOR_PARAMS["RSI_PERIOD"]))
        macd = unwrap(ta.macd(df['close'], fast=INDICATOR_PARAMS["MACD_FAST"],
                              slow=INDICATOR_PARAMS["MACD_SLOW"],
                              signal=INDICATOR_PARAMS["MACD_SIGNAL"]))
        stoch = unwrap(ta.stoch(df['high'], df['low'], df['close'], k=INDICATOR_PARAMS["STOCH_K_PERIOD"]))
        adx = unwrap(ta.adx(df['high'], df['low'], df['close'], length=INDICATOR_PARAMS["ADX_PERIOD"]))
        cci = unwrap(ta.cci(df['high'], df['low'], df['close'], length=INDICATOR_PARAMS["CCI_PERIOD"]))
        ichimoku = unwrap(ta.ichimoku(df['high'], df['low'], df['close'],
                                      tenkan=INDICATOR_PARAMS["ICHIMOKU_CONVERSION"],
                                      kijun=INDICATOR_PARAMS["ICHIMOKU_BASE"]))
        obv = unwrap(ta.obv(df['close'], df['volume']))

        slope_angle = calc_slope(df['close'].iloc[-INDICATOR_PARAMS["LR_PERIOD"]:]) \
                      if not df['close'].iloc[-INDICATOR_PARAMS["LR_PERIOD"]:].empty else 0.0
        last_time = df.index[-1].isoformat()

        metrics = {
            'ATR_14': safe_last_value(atr),
            'EMA_14': safe_last_value(ema14),
            'EMA_200': safe_last_value(ema200),
            'Bollinger_upper': safe_last_value(bb, key='BBU_20_2.0'),
            'Bollinger_middle': safe_last_value(bb, key='BBM_20_2.0'),
            'Bollinger_lower': safe_last_value(bb, key='BBL_20_2.0'),
            'Heiken_Ashi_open': safe_last_value(ha_df['HA_open']),
            'Heiken_Ashi_high': safe_last_value(ha_df['HA_high']),
            'Heiken_Ashi_low': safe_last_value(ha_df['HA_low']),
            'Heiken_Ashi_close': safe_last_value(ha_df['HA_close']),
            'Linear_Regression_slope_angle': slope_angle,
            'RSI': safe_last_value(rsi),
            'MACD': safe_last_value(macd, key='MACD_12_26_9'),
            'MACD_signal': safe_last_value(macd, key='MACDs_12_26_9'),
            'MACD_hist': safe_last_value(macd, key='MACDh_12_26_9'),
            'Stochastic_k': safe_last_value(stoch, key='STOCHk_14_3_3'),
            'Stochastic_d': safe_last_value(stoch, key='STOCHd_14_3_3'),
            'ADX': safe_last_value(adx, key='ADX_14'),
            'CCI': safe_last_value(cci),
            'Ichimoku_tenkan': safe_last_value(ichimoku, key='ISA_9'),
            'Ichimoku_kijun': safe_last_value(ichimoku, key='ISB_26'),
            'OBV': safe_last_value(obv)
        }

        return {
            'calculation_time': datetime.utcnow().isoformat(),
            'hour_utc': last_time,
            'symbol': symbol,
            'metrics': metrics
        }
    except Exception as e:
        raise ValueError(f"Error calculating indicators for {symbol}: {e}")
