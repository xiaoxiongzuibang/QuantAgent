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
def get_fundamental_data(tickers: list[str]):
    """获取基本面数据（最近一期年报 + TTM）"""
    df = get_fundamentals(tickers)
    return df.to_dict()

@mcp.tool()
def compute_book_to_price(tickers: list[str]):
    """计算 B/P 基本面因子"""
    df = get_fundamentals(tickers)
    factor = calc_book_to_price(df)
    return factor.to_dict()

@mcp.tool()
def compute_pe_inverse(tickers: list[str]):
    """计算 E/P 基本面因子"""
    df = get_fundamentals(tickers)
    factor = calc_pe_inverse(df)
    return factor.to_dict()

@mcp.tool()
def compute_dividend_yield(tickers: list[str]):
    """计算股息率因子"""
    df = get_fundamentals(tickers)
    factor = calc_dividend_yield(df)
    return factor.to_dict()

@mcp.tool()
def compute_roe(tickers: list[str]):
    """计算 ROE（净资产收益率）"""
    df = get_fundamentals(tickers)
    factor = calc_roe(df)
    return factor.to_dict()

if __name__ == "__main__":
    mcp.run("stdio")
