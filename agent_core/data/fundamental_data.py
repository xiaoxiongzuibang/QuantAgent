import pandas as pd, yfinance as yf
from typing import List

def get_fundamental_data(tickers: List[str]) -> pd.DataFrame:
    """
    拉取多支股票最近一期年报 + TTM 估值数据
    返回 DataFrame：
        columns = MultiIndex[ticker, field, period]
        index   = [report_date]（统一用最近年报日期）
    """
    all_frames = []

    for tk in tickers:
        tkr = yf.Ticker(tk)

        # ① 年报最近一期
        bs_latest = tkr.balance_sheet.iloc[:, 0]     # Series
        is_latest = tkr.financials.iloc[:, 0]
        cf_latest = tkr.cashflow.iloc[:, 0]

        annual = pd.concat([is_latest, bs_latest, cf_latest])
        annual.name = tkr.balance_sheet.columns[0]   # 把列日期作为行索引
        annual_df = annual.to_frame().T              # 变 DataFrame，只有 1 行

        # ② 关键统计 (TTM / 当前)
        info = tkr.info
        stat = pd.Series(
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

        # ③ 统一列多级索引
        annual_df.columns = pd.MultiIndex.from_product(
            [[tk], annual_df.columns, ["annual"]],
            names=["ticker", "field", "period"],
        )
        stat.columns = pd.MultiIndex.from_product(
            [[tk], stat.columns, ["ttm"]],
            names=["ticker", "field", "period"],
        )

        all_frames.append(pd.concat([annual_df, stat], axis=1))

    fundamentals = pd.concat(all_frames, axis=1)
    fundamentals.index.name = "report_date"
    return fundamentals