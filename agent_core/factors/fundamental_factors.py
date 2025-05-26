# agent_core/factors/fundamental_factors.py
import pandas as pd


def calc_book_to_price(fund_df: pd.DataFrame) -> pd.Series:
    """
    市净率反转因子（B/P） = 净资产 / 当前市值
    """
    book = fund_df.xs("bookValue", level="field", axis=1).xs("annual", level="period", axis=1).iloc[0]
    market_cap = fund_df.xs("marketCap", level="field", axis=1).xs("ttm", level="period", axis=1).iloc[0]
    return book / market_cap


def calc_pe_inverse(fund_df: pd.DataFrame) -> pd.Series:
    """
    市盈率倒数因子（E/P） = 每股收益 / 当前价格
    """
    pe = fund_df.xs("trailingPE", level="field", axis=1).xs("ttm", level="period", axis=1).iloc[0]
    return 1 / pe


def calc_dividend_yield(fund_df: pd.DataFrame) -> pd.Series:
    """
    股息率因子 = 股息 / 当前股价
    """
    return fund_df.xs("dividendYield", level="field", axis=1).xs("ttm", level="period", axis=1).iloc[0]


def calc_roe(fund_df: pd.DataFrame) -> pd.Series:
    """
    净资产收益率（ROE） = 净利润 / 股东权益
    """
    net_income = fund_df.xs("netIncome", level="field", axis=1).xs("annual", level="period", axis=1).iloc[0]
    equity = fund_df.xs("bookValue", level="field", axis=1).xs("annual", level="period", axis=1).iloc[0]
    return net_income / equity