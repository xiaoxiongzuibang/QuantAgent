import pandas as pd, yfinance as yf
from typing import List

# def get_fundamental_data(tickers: List[str]) -> pd.DataFrame:
#     """
#     拉取多支股票最近一期年报 + TTM 估值数据
#     返回 DataFrame：
#         columns = MultiIndex[ticker, field, period]
#         index   = [report_date]（统一用最近年报日期）
#     """
#     all_frames = []

#     for tk in tickers:
#         tkr = yf.Ticker(tk)

#         # ① 年报最近一期
#         bs_latest = tkr.balance_sheet.iloc[:, 0]     # Series
#         is_latest = tkr.financials.iloc[:, 0]
#         cf_latest = tkr.cashflow.iloc[:, 0]

#         annual = pd.concat([is_latest, bs_latest, cf_latest])
#         annual.name = tkr.balance_sheet.columns[0]   # 把列日期作为行索引
#         annual_df = annual.to_frame().T              # 变 DataFrame，只有 1 行

#         # ② 关键统计 (TTM / 当前)
#         info = tkr.info
#         stat = pd.Series(
#             {
#                 "trailingPE":    info.get("trailingPE"),
#                 "forwardPE":     info.get("forwardPE"),
#                 "priceToBook":   info.get("priceToBook"),
#                 "dividendYield": info.get("dividendYield"),
#                 "marketCap":     info.get("marketCap"),
#                 "beta":          info.get("beta"),
#             },
#             name="ttm",
#         ).to_frame().T

#         # ③ 统一列多级索引
#         annual_df.columns = pd.MultiIndex.from_product(
#             [[tk], annual_df.columns, ["annual"]],
#             names=["ticker", "field", "period"],
#         )
#         stat.columns = pd.MultiIndex.from_product(
#             [[tk], stat.columns, ["ttm"]],
#             names=["ticker", "field", "period"],
#         )

#         all_frames.append(pd.concat([annual_df, stat], axis=1))

#     fundamentals = pd.concat(all_frames, axis=1)
#     fundamentals.index.name = "report_date"
#     return fundamentals

import pandas as pd
import yfinance as yf
from typing import List, Literal, Optional

# ============================ #
#   基础工具函数
# ============================ #
def _get_report_by_period(df: pd.DataFrame, period: str) -> pd.Series:
    if not isinstance(period, str):
        raise TypeError(f"Invalid period type: {type(period)}. Must be a string like 'latest' or '2023-12-31'.")

    if period == "latest":
        return df.iloc[:, 0]
    elif period in df.columns:
        return df[period]
    else:
        raise ValueError(f"Period '{period}' not available. Available: {list(df.columns)}")


# ============================ #
#   获取不同类型的财务报表
# ============================ #
def get_income_statement(ticker: str, period: str = "latest") -> pd.DataFrame:
    tkr = yf.Ticker(ticker)
    is_data = _get_report_by_period(tkr.financials, period)
    df = is_data.to_frame().T
    df.index.name = "report_date"
    df.columns = pd.MultiIndex.from_product(
        [[ticker], df.columns, ["income"]],
        names=["ticker", "field", "report_type"]
    )
    return df

def get_balance_sheet(ticker: str, period: str = "latest") -> pd.DataFrame:
    tkr = yf.Ticker(ticker)
    bs_data = _get_report_by_period(tkr.balance_sheet, period)
    df = bs_data.to_frame().T
    df.index.name = "report_date"
    df.columns = pd.MultiIndex.from_product(
        [[ticker], df.columns, ["balance"]],
        names=["ticker", "field", "report_type"]
    )
    return df

def get_cashflow_statement(ticker: str, period: str = "latest") -> pd.DataFrame:
    tkr = yf.Ticker(ticker)
    cf_data = _get_report_by_period(tkr.cashflow, period)
    df = cf_data.to_frame().T
    df.index.name = "report_date"
    df.columns = pd.MultiIndex.from_product(
        [[ticker], df.columns, ["cashflow"]],
        names=["ticker", "field", "report_type"]
    )
    return df


# ============================ #
#   获取估值指标（TTM）
# ============================ #
def get_valuation_metrics(ticker: str) -> pd.DataFrame:
    tkr = yf.Ticker(ticker)
    info = tkr.info
    df = pd.Series(
        {
            "trailingPE":    info.get("trailingPE"),
            "forwardPE":     info.get("forwardPE"),
            "priceToBook":   info.get("priceToBook"),
            "dividendYield": info.get("dividendYield"),
            "marketCap":     info.get("marketCap"),
            "beta":          info.get("beta"),
        },
        name="ttm",
    ).to_frame().T
    df.columns = pd.MultiIndex.from_product(
        [[ticker], df.columns, ["valuation"]],
        names=["ticker", "field", "report_type"]
    )
    df.index.name = "report_date"
    return df


# ============================ #
#   主函数：按需组合信息
# ============================ #
def get_fundamental_data(
    tickers: List[str],
    period: str = "latest",
    include: Optional[List[Literal["income", "balance", "cashflow", "valuation"]]] = None,
) -> pd.DataFrame:
    if include is None:
        include = ["income", "balance", "cashflow", "valuation"]

    all_frames = []

    for ticker in tickers:
        frames = []
        if "income" in include:
            frames.append(get_income_statement(ticker, period))
        if "balance" in include:
            frames.append(get_balance_sheet(ticker, period))
        if "cashflow" in include:
            frames.append(get_cashflow_statement(ticker, period))
        if "valuation" in include:
            frames.append(get_valuation_metrics(ticker))

        all_frames.append(pd.concat(frames, axis=1))

    result = pd.concat(all_frames, axis=1)
    result.index.name = "report_date"
    return result
