import numpy as np, pandas as pd
from typing import Sequence
from .factor import calc_factors
from .data import get_prices

def _rank_zscore(df: pd.DataFrame, ascending=True) -> pd.DataFrame:
    return df.rank(axis=1, ascending=ascending).apply(lambda x: (x - x.mean())/x.std(), axis=1)

def build_score(factor_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    scores = []
    for name, df in factor_dict.items():
        asc = False if name == "value" else True   # value 越大越好，其余相反
        scores.append(_rank_zscore(df, ascending=asc))
    return sum(scores) / len(scores)

def run(factors: Sequence[str], start: str, end: str, top_n: int = 30) -> pd.Series:
    factor_data = calc_factors(list(factors))
    score = build_score(factor_data).loc[start:end]

    close = get_prices().xs("close", level=1, axis=1).loc[start:end]
    rets  = close.pct_change().shift(-1)                     # 次日收益

    # 每月调仓：取月末行
    month_ends = score.resample("M").last().index
    holdings = (score.loc[month_ends]
                   .apply(lambda x: x.nlargest(top_n).index, axis=1))

    # 构造持仓矩阵
    weight = pd.DataFrame(0, index=score.index, columns=score.columns, dtype=float)
    for date, tickers in holdings.items():
        weight.loc[date, tickers] = 1 / top_n
    weight = weight.ffill()

    portfolio_ret = (weight.shift().mul(rets)).sum(axis=1)
    return (1 + portfolio_ret).cumprod()

