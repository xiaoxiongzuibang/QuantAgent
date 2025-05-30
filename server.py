# mcp_servers/market_data/server.py
from typing import Optional, Dict, Any
from fastmcp import FastMCP
import pandas as pd

from agent_core.data.price_data import *
from agent_core.data.fundamental_data import *
from agent_core.data.macro_data import *

from agent_core.factors.tech_factors import *
from agent_core.factors.fundamental_factors import *
from agent_core.backtest.factor_backtest import *

mcp = FastMCP("quant-agent")

@mcp.tool()
def download_prices(tickers: list[str], start: str, end: str):
    """下载价格数据（支持多支资产）"""
    df = get_res_data(tickers, start, end)
    return df.tail().to_dict()

@mcp.tool()
def compute_rsi(ticker: str, start: str, end: str, window: int = 14):
    """计算 RSI 技术指标"""
    df = get_res_data(ticker, start, end)
    rsi = calc_rsi(df["close"], window)
    return rsi.dropna().to_dict()

@mcp.tool()
def compute_macd(ticker: str, start: str, end: str):
    """计算 MACD 技术指标"""
    df = get_res_data(ticker, start, end)
    macd = calc_macd(df["close"])
    return macd.dropna().to_dict(orient="list")

@mcp.tool()
def simple_backtest(ticker: str, start: str, end: str):
    """示例回测：用动量因子构建组合回测"""
    price_df = get_res_data(ticker, start, end)
    momentum = calc_momentum(price_df["close"])
    momentum.name = "score"

    factor = momentum.dropna()
    factor.index = pd.MultiIndex.from_product([[i.strftime("%Y-%m-%d") for i in factor.index], [ticker]])

    # reshape price to multiindex
    price_df.columns = pd.MultiIndex.from_product([[col for col in price_df.columns], [ticker]])

    nav = backtest_equal_weight(factor, price_df)
    return nav.to_dict()

@mcp.tool()
def income_statement(ticker: str, period: str = "latest") -> dict:
    """Get income statement for a stock ticker. Period must be 'latest' or a string like '2023-12-31'."""
    df = get_income_statement(ticker, period)
    return df.to_dict()


@mcp.tool()
def balance_sheet(ticker: str, period: str = "latest"):
    """Get the balance sheet for a stock ticker and a specific period."""
    df = get_balance_sheet(ticker, period)
    return df.tail().to_dict()

@mcp.tool()
def cashflow_statement(ticker: str, period: str = "latest"):
    """Get the cashflow statement for a stock ticker and a specific period."""
    df = get_cashflow_statement(ticker, period)
    return df.tail().to_dict()

@mcp.tool()
def valuation_metrics(ticker: str):
    """Get valuation metrics (e.g., PE ratio, market cap) for a stock."""
    df = get_valuation_metrics(ticker)
    return df.tail().to_dict()

@mcp.tool()
def fundamental_data(
    tickers: list[str],
    period: str = "latest",
    include: list[str] = ["income", "balance", "cashflow", "valuation"]
):
    """Get fundamental data (income, balance, cashflow, valuation) for one or more tickers."""
    df = get_fundamental_data(tickers, period, include)
    return df.tail().to_dict()

@mcp.tool()
def macro_data(indicators: list[str], start: str = "2000-01-01", end: str = None):
    """
    获取指定宏观经济指标数据（如GDP、CPI等）。
    """
    df = get_macro_dataset(indicators, start, end)
    return df.tail().to_dict()



if __name__ == "__main__":
    mcp.run("stdio")
