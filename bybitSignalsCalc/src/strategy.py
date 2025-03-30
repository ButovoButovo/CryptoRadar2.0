from datetime import datetime

def generate_trade_signal(result: dict) -> dict:
    """
    Генерирует торговой сигнал на основе комплексного набора метрик.
    Используются:
      - Трендовые: EMA14, EMA200, Ichimoku (Tenkan, Kijun), линейная регрессия и Heiken Ashi
      - Импульсные: RSI, MACD, MACD_hist, Стохастик (%K и %D), CCI
      - Объём/волатильность: ADX, OBV, Bollinger Bands, ATR
    Комиссия (0.1% на вход + 0.1% на выход) учитывается при расчёте стоп-лосса и целевого профита.
    """
    metrics = result['metrics']
    symbol = result['symbol']
    entry_price = metrics['Heiken_Ashi_close']

    # Трендовые условия
    trend_buy = (
        metrics['EMA_14'] > metrics['EMA_200'] and
        metrics['Ichimoku_tenkan'] > metrics['Ichimoku_kijun'] and
        metrics['Linear_Regression_slope_angle'] > 0 and
        entry_price > metrics['EMA_200'] and
        (metrics['Heiken_Ashi_close'] > metrics['Heiken_Ashi_open'])
    )
    trend_sell = (
        metrics['EMA_14'] < metrics['EMA_200'] and
        metrics['Ichimoku_tenkan'] < metrics['Ichimoku_kijun'] and
        metrics['Linear_Regression_slope_angle'] < 0 and
        entry_price < metrics['EMA_200'] and
        (metrics['Heiken_Ashi_close'] < metrics['Heiken_Ashi_open'])
    )

    # Импульсные условия
    momentum_buy = (
        metrics['RSI'] > 30 and metrics['RSI'] < 70 and
        metrics['MACD'] > metrics['MACD_signal'] and
        (metrics['MACD_hist'] > 0) and
        (metrics['Stochastic_k'] < 20 and metrics['Stochastic_d'] < 20) and
        (metrics['CCI'] < 0)
    )
    momentum_sell = (
        metrics['RSI'] > 70 and
        metrics['MACD'] < metrics['MACD_signal'] and
        (metrics['MACD_hist'] < 0) and
        (metrics['Stochastic_k'] > 80 and metrics['Stochastic_d'] > 80) and
        (metrics['CCI'] > 0)
    )

    # Объём и волатильность
    adx_confirm = (metrics['ADX'] >= 25)
    vol_buy = (entry_price <= metrics['Bollinger_lower'] * 1.01)
    vol_sell = (entry_price >= metrics['Bollinger_upper'] * 0.99)
    bb_filter_buy = (entry_price < metrics['Bollinger_middle'])
    bb_filter_sell = (entry_price > metrics['Bollinger_middle'])
    obv_filter_buy = (metrics['OBV'] > 0)
    obv_filter_sell = (metrics['OBV'] < 0)

    buy_conditions = (trend_buy and momentum_buy and adx_confirm and vol_buy and bb_filter_buy and obv_filter_buy)
    sell_conditions = (trend_sell and momentum_sell and adx_confirm and vol_sell and bb_filter_sell and obv_filter_sell)

    signal = "NONE"
    stop_loss = None
    target_profit = None
    risk = None

    atr = metrics['ATR_14']
    multiplier = 1.5
    commission = entry_price * 0.002  # 0.2%

    if buy_conditions:
        signal = "BUY"
        risk = atr * multiplier + commission
        stop_loss = entry_price - risk
        target_profit = entry_price + risk * 2.5
    elif sell_conditions:
        signal = "SELL"
        risk = atr * multiplier + commission
        stop_loss = entry_price + risk
        target_profit = entry_price - risk * 2.5

    return {
        "symbol": symbol,
        "signal": signal,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target_profit": target_profit,
        "risk": risk,
        "timestamp": datetime.now().isoformat()
    }
