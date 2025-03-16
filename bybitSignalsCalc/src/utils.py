# src/utils.py
from typing import Any, List, Optional
import numpy as np
import pandas as pd
from decimal import Decimal

def unwrap(result: Any) -> Any:
    """Возвращает первый элемент кортежа, если результат — кортеж, иначе возвращает результат."""
    return result[0] if isinstance(result, tuple) else result

def safe_float(value: Any) -> Optional[float]:
    """Преобразует значение в float, если оно не None."""
    try:
        return float(value) if value is not None else None
    except Exception:
        return None

def safe_last_value(series: pd.Series, key: Optional[str] = None, offset: int = 0) -> Optional[float]:
    """
    Извлекает значение из ряда с учетом смещения offset (0 – последний элемент, 1 – предпоследний и т.д.).
    Если ключ key указан, извлекается значение по ключу.
    """
    if series.empty or len(series) <= offset:
        return None
    row = series.iloc[-1 - offset]
    if key is not None:
        if isinstance(row, (pd.Series, dict)):
            value = row.get(key, None)
            return safe_float(value)
        return safe_float(row)
    if isinstance(row, pd.Series) and len(row) == 1:
        row = row.iloc[0]
    return safe_float(row)

def convert_decimal_to_float(data: List[Any]) -> List[Any]:
    """
    Преобразует список строк, где значения Decimal заменяются на float.
    """
    return [
        (
            row[0],
            float(row[1]) if isinstance(row[1], Decimal) else row[1],
            float(row[2]) if isinstance(row[2], Decimal) else row[2],
            float(row[3]) if isinstance(row[3], Decimal) else row[3],
            float(row[4]) if isinstance(row[4], Decimal) else row[4],
            float(row[5]) if isinstance(row[5], Decimal) else row[5],
        )
        for row in data
    ]

def convert_decimal_to_float_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Векторное преобразование столбцов, содержащих Decimal, в float.
    Предполагается, что столбцы: open, high, low, close, volume.
    """
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def calc_slope(series: pd.Series) -> float:
    """Расчет угла наклона в градусах для заданного ряда."""
    x = np.arange(len(series))
    coeff = np.polyfit(x, series.values.astype(float), 1)
    return np.degrees(np.arctan(coeff[0]))

def heiken_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Рассчитывает Heiken-Ashi на основе столбцов open, high, low, close.
    Формулы:
      HA_close = (open + high + low + close) / 4
      HA_open = (предыдущий HA_open + предыдущий HA_close) / 2 (для первой строки — open)
      HA_high = максимум из high, HA_open, HA_close
      HA_low = минимум из low, HA_open, HA_close
    """
    ha = pd.DataFrame(index=df.index, columns=["HA_open", "HA_high", "HA_low", "HA_close"])
    ha["HA_close"] = (df["open"] + df["high"] + df["low"] + df["close"]) / 4
    ha.iloc[0, ha.columns.get_loc("HA_open")] = df.iloc[0]["open"]
    for i in range(1, len(df)):
        ha.iloc[i, ha.columns.get_loc("HA_open")] = 0.5 * (ha.iloc[i-1]["HA_open"] + ha.iloc[i-1]["HA_close"])
    ha["HA_high"] = pd.concat([df["high"], ha["HA_open"], ha["HA_close"]], axis=1).max(axis=1)
    ha["HA_low"] = pd.concat([df["low"], ha["HA_open"], ha["HA_close"]], axis=1).min(axis=1)
    return ha
