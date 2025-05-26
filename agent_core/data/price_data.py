import numpy as np, yfinance as yf, pandas as pd
from typing import Union, List

def get_single_res_data(ticker: str, start: str, end: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        return {"error": "找不到该股票或时间段无数据"}
    return df

def get_multi_res_data(tickers, start, end):
    df = yf.download(
        tickers,
        start=start,
        end=end,
        group_by="ticker",        # ⚠️ 关键参数！
        auto_adjust=True,
        progress=False,
        threads=True
    )

    # 检查结构：如果不是 MultiIndex，raise error
    if not isinstance(df.columns, pd.MultiIndex):
        raise ValueError("Expected MultiIndex columns. Try upgrading yfinance or check ticker list.")

    # 现在是 columns = (ticker, field)，需要变成 (field, ticker)
    df = df.swaplevel(axis=1).sort_index(axis=1)
    return df


def get_res_data(tickers: Union[str, List[str]], start: str, end: str) -> pd.DataFrame:
    """
    获取一支或多支资产的价格数据（open/high/low/close/volume）

    参数:
        tickers: str 或 list[str]，可以是单个或多个资产代码
        start: 起始日期
        end: 结束日期

    返回:
        - 如果是单支股票: DataFrame，columns = [open, high, low, close, volume]
        - 如果是多支股票: DataFrame，columns = MultiIndex[level 0: field, level 1: ticker]
    """
    single = False
    if isinstance(tickers, str):
        tickers = [tickers]
        single = True

    df = yf.download(
        tickers,
        start=start,
        end=end,
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True
    )

    if df.empty:
        raise ValueError("下载失败：数据为空")

    # 判断是否是多只股票结构
    if isinstance(df.columns, pd.MultiIndex):
        # 多支资产：原结构是 (ticker, field)，我们转为 (field, ticker)
        df = df.swaplevel(axis=1).sort_index(axis=1)

        # 清洗列名：全部小写
        df.columns = pd.MultiIndex.from_tuples(
            [(f.lower().strip(), t.strip()) for f, t in df.columns],
            names=["field", "ticker"]
        )

        # 只保留我们需要的字段
        fields = ["open", "high", "low", "close", "volume"]
        df = df.loc[:, df.columns.get_level_values("field").isin(fields)]
        df = df.replace([np.inf, -np.inf], np.nan).dropna(how="all")

        if single:
            # 如果用户只给了一个 ticker，也返回普通结构（扁平）
            df = df.xs(tickers[0], level="ticker", axis=1)

    else:
        # 单支股票，但列是平面的
        df.columns = [c.strip().lower() for c in df.columns]
        if "adj close" in df.columns and "close" not in df.columns:
            df["close"] = df["adj close"]

        needed = ["open", "high", "low", "close", "volume"]
        df = df[needed]
        df = df.replace([np.inf, -np.inf], np.nan).dropna(how="all")

    if len(df) < 30:
        raise ValueError("数据不足 30 行")

    return df


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


def get_metrics(ticker: str, start: str, end: str) -> dict:
    try:
        df = get_res_data(ticker, start, end)
        df = clean_df(df)
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



