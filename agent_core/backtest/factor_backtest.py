# agent_core/backtest/factor_backtest.py
import pandas as pd
import numpy as np


def calc_ic(factor: pd.Series, future_ret: pd.Series, method: str = "spearman") -> float:
    """
    计算信息系数（IC）：因子值与未来收益的横截面相关性
    """
    aligned = pd.concat([factor, future_ret], axis=1).dropna()
    if aligned.empty:
        return np.nan
    return aligned.corr(method=method).iloc[0, 1]


def group_backtest(factor: pd.Series, future_ret: pd.Series, n_groups: int = 5) -> pd.Series:
    """
    将因子分成 n_groups 组，计算每组未来收益均值（横截面）
    返回：Series(index=group_label, value=mean_return)
    """
    aligned = pd.concat([factor, future_ret], axis=1).dropna()
    aligned["group"] = pd.qcut(aligned.iloc[:, 0], q=n_groups, labels=False)
    return aligned.groupby("group").mean().iloc[:, 1]


def backtest_equal_weight(factor_panel: pd.Series, price_panel: pd.DataFrame, top_pct: float = 0.2) -> pd.Series:
    """
    简单回测：每期买入因子得分 top_pct 的股票，等权持有一周期
    输入：
      factor_panel: MultiIndex[date, ticker] 的因子值
      price_panel: MultiIndex[field, ticker] 的收盘价（需要 ['close', ...]）
    返回：净值序列（Series，index=date）
    """
    factor_panel = factor_panel.dropna()
    nav = []
    dates = sorted(factor_panel.index.get_level_values(0).unique())

    for i in range(len(dates) - 1):
        date = dates[i]
        next_date = dates[i + 1]

        daily_scores = factor_panel.loc[date]
        top = daily_scores.nlargest(int(len(daily_scores) * top_pct))
        tickers = top.index.tolist()

        try:
            p0 = price_panel.loc["close", tickers].loc[date]
            p1 = price_panel.loc["close", tickers].loc[next_date]
        except KeyError:
            continue

        ret = (p1 - p0) / p0
        nav.append((1 + ret.mean()) if nav == [] else nav[-1] * (1 + ret.mean()))

    return pd.Series(nav, index=dates[1:])
