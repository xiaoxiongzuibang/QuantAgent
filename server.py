from typing import Optional, Dict, Any
from fastmcp import FastMCP
import pandas as pd

from agent_core.data.price_data import *
from agent_core.data.fundamental_data import *
from agent_core.data.macro_data import *

from agent_core.factors.tech_factors import *
from agent_core.factors.fundamental_factors import *

from agent_core.strategy.strategy_builder import *
from agent_core.backtest.factor_backtest import *

from agent_core.factors.factor_registry import *


mcp = FastMCP("quant-agent")

# ===== Data Module =====
@mcp.tool()
def download_prices(tickers: list[str], start: str, end: str):
    """下载价格数据（支持多支资产）"""
    df = get_res_price_data(tickers, start, end)
    return df.tail().to_dict()


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

# ===== Backtest Module =====
@mcp.tool()
def run_backtest_with_factor(factor_name: str, stock_universe: list, start_date: str, end_date: str) -> dict:
    """
    用指定的因子，在指定股票池和时间范围上进行回测
    """
    price_df = get_res_price_data(stock_universe, start=start_date, end=end_date)

    factor_df = get_factor(factor_name, price_df)  # ← 会做 strip + lower + 映射

    signal_df = generate_top_n_signal(factor_df, top_n=10)
    weight_df = equal_weight(signal_df)
    equity = backtest(price_df, weight_df)

    return equity.to_dict()



if __name__ == "__main__":
    mcp.run("stdio")
