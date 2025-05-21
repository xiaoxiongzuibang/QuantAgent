import os
import json
import uuid
import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
import backtrader as bt
from openai import OpenAI
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend
import matplotlib.pyplot as plt

# ---------- Function Calling Definitions ----------
functions = [
    {
        "name": "update_strategy_params",
        "description": "Collect or update strategy parameters in memory",
        "parameters": {
            "type": "object",
            "properties": {
                "indicator": {"type": "string"},
                "buy_rule":  {"type": "string"},
                "sell_rule": {"type": "string"},
                "ticker":    {"type": "string"},
                "start":     {"type": "string"},
                "end":       {"type": "string"}
            }
        }
    },
    {
        "name": "plot_stock_chart",
        "description": "Generate a line chart of stock close prices",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start":  {"type": "string"},
                "end":    {"type": "string"}
            },
            "required": ["ticker", "start", "end"]
        }
    },
    {
        "name": "get_metrics",
        "description": "Compute common quant metrics (Sharpe ratio, max drawdown, volatility, return)",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start":  {"type": "string"},
                "end":    {"type": "string"}
            },
            "required": ["ticker", "start", "end"]
        }
    },
    {
        "name": "run_backtest",
        "description": "Run backtest based on current memory.strategy settings",
        "parameters": {
            "type": "object",
            "properties": {"strategy": {"type": "object"}},
            "required": ["strategy"]
        }
    }
]

# ---------- Memory ----------
memory = {
    "strategy": {k: None for k in ("indicator","buy_rule","sell_rule","ticker","start","end")},
    "cache": {}
}

# ---------- Data Cleaning ----------
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

# ---------- Plotting ----------
def plot_line_chart(ticker: str, start: str, end: str) -> dict:
    try:
        df = get_cleaned_data(ticker, start, end)
    except Exception as e:
        return {"error": str(e)}
    plt.figure(figsize=(10,4))
    plt.plot(df.index, df["close"], label=f"{ticker} Close Price")
    plt.title(f"{ticker} Price from {start} to {end}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.tight_layout()
    path = f"line_{uuid.uuid4().hex[:8]}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return {"image": path}

# ---------- Metrics ----------
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

# ---------- Backtest ----------
from mycerebro import MyCerebro

def make_bt_strategy(cfg):
    class DynStrat(bt.Strategy):
        def __init__(self):
            ind = cfg["indicator"].lower()
            if ind in ("sma","ema"):
                cls = bt.ind.SMA if ind=="sma" else bt.ind.EMA
                self.fast = cls(period=5)
                self.slow = cls(period=20)
            elif ind == "rsi":
                self.rsi = bt.ind.RSI(period=14)
            elif ind == "macd":
                self.macd = bt.ind.MACD()
        def next(self):
            if not self.position and (_buy(cfg,self)):
                self.buy()
            elif self.position and (_sell(cfg,self)):
                self.close()
    return DynStrat

def _buy(c, s):
    return ((hasattr(s,"fast") and s.fast[0]>s.slow[0] and s.fast[-1]<=s.slow[-1])
            or (hasattr(s,"rsi") and s.rsi[0]<30)
            or (hasattr(s,"macd") and s.macd.macd[0]>s.macd.signal[0]))

def _sell(c, s):
    return ((hasattr(s,"fast") and s.fast[0]<s.slow[0] and s.fast[-1]>=s.slow[-1])
            or (hasattr(s,"rsi") and s.rsi[0]>70)
            or (hasattr(s,"macd") and s.macd.macd[0]<s.macd.signal[0]))

def run_backtest(cfg: dict) -> dict:
    today = dt.date.today().strftime("%Y-%m-%d")
    raw = yf.download(cfg["ticker"], cfg["start"], min(cfg["end"], today), auto_adjust=False, progress=False)
    if raw.empty:
        return {"error": "no data"}
    try:
        data = clean_df(raw)
    except ValueError as e:
        return {"error": str(e)}
    cerebro = MyCerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=data))
    cerebro.addstrategy(make_bt_strategy(cfg))
    cerebro.broker.setcash(100000)
    cerebro.run()
    fig = cerebro.plot(style='candlestick')[0][0]
    img = f"bt_{uuid.uuid4().hex[:8]}.png"
    fig.savefig(img, dpi=150, bbox_inches='tight')
    plt.close(fig)
    equity = cerebro.broker.getvalue()
    return {
        "summary": f"Final equity ${equity:,.2f} (PnL ${equity-100000:,.2f})",
        "image": img
    }

# ---------- Strategy Params ----------
def update_strategy_params(**kwargs) -> dict:
    memory["strategy"].update({k: v for k, v in kwargs.items() if v is not None})
    missing = [k for k, v in memory["strategy"].items() if v is None]
    return {"missing": missing}

# ---------- OpenAI Client ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt(msgs: list):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=msgs,
        functions=functions,
        function_call="auto"
    ).choices[0].message
