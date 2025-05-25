import pandas as pd
from .data import get_prices, pct_change

def book_to_market() -> pd.DataFrame:
    """示例：直接用你数据里的 bm 列。"""
    prices = get_prices()
    return prices.xs("bm", level=1, axis=1)          # (date, ticker)→bm

def momentum(window: int = 252) -> pd.DataFrame:
    close = get_prices().xs("close", level=1, axis=1)
    return pct_change(close, window)

_FACTOR_REGISTRY = {
    "value": book_to_market,       # 低→成长，高→价值
    "momentum": momentum,
}

def calc_factors(factor_names: list[str]) -> dict[str, pd.DataFrame]:
    return {name: _FACTOR_REGISTRY[name]() for name in factor_names}
