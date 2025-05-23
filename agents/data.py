import numpy as np, yfinance as yf, pandas as pd
from .memory import memory

def get_stock_stats_core(ticker: str, start: str, end: str) -> dict:
    """
    获取某支股票在指定时间段内的收盘价的描述统计
    """
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        return {"error": "找不到该股票或时间段无数据"}
    return df["Adj Close"].describe().to_dict()

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names, ensure open/high/low/close/volume present,
    convert to numeric, ffill, dropna, enforce minimum length.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [t[0].strip().lower() for t in df.columns]
    else:
        df.columns = [c.strip().lower() for c in df.columns]
    if "close" not in df.columns and "adjclose" in df.columns:
        df["close"] = df["adjclose"]
    need = ["open","high","low","close","volume"]
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise ValueError(f"Missing columns: {miss}")
    df = df[need].apply(pd.to_numeric, errors="coerce").ffill().dropna()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    if len(df) < 30:
        raise ValueError("Not enough data (<30 bars)")
    return df

def get_cleaned_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Download, clean, and cache data for given ticker and date range.
    """
    key = f"{ticker}_{start}_{end}"
    if key not in memory["cache"]:
        raw = yf.download(ticker, start=start, end=end, progress=False)
        if raw.empty:
            raise ValueError("No data for given range")
        df = clean_df(raw)
        memory["cache"][key] = df
    return memory["cache"][key]

def get_metrics(ticker: str, start: str, end: str) -> dict:
    try:
        df = get_cleaned_data(ticker, start, end)
    except Exception as e:
        return {"error": str(e)}
    returns = df["close"].pct_change().dropna()
    cum = (1 + returns).cumprod()
    sharpe = returns.mean() / returns.std() * np.sqrt(252)
    max_dd = (cum / cum.cummax() - 1).min()
    vol = returns.std() * np.sqrt(252)
    total_ret = cum.iloc[-1] - 1
    return {
        "sharpe_ratio": round(sharpe,3),
        "max_drawdown": round(max_dd,3),
        "volatility": round(vol,3),
        "return": round(total_ret,3)
    }
