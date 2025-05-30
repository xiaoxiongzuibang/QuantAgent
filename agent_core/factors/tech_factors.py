# agent_core/factors/tech_factors.py
import pandas as pd
import numpy as np

def calc_momentum(price_df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    动量因子：当前价格相对于 N 日前的涨幅百分比
    """
    momentum = price_df['close'].pct_change(periods=window)
    return momentum

def calc_volatility(price_df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    波动率因子：过去 N 日的对数收益标准差
    """
    log_return = np.log(price_df['close'] / price_df['close'].shift(1))
    vol = log_return.rolling(window=window).std()
    return vol

def calc_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    相对强弱指数 RSI
    说明：衡量上涨动能与下跌动能的相对比率，常用于判断超买超卖状态。
    返回值范围 0-100，>70 通常视为超买，<30 为超卖。
    """
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    MACD 指标（指数平滑异同移动平均线）
    fast EMA - slow EMA = DIF
    signal = DIF 的 EMA
    MACD = DIF - signal
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = dif - dea

    return pd.DataFrame({
        "DIF": dif,
        "DEA": dea,
        "MACD": macd
    })






