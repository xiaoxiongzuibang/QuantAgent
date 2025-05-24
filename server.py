# mcp_servers/market_data/server.py

from fastmcp import FastMCP
from agents.data import *
from agents.plot import *
from agents.backtest import *
from agents.memory import *

mcp = FastMCP("quant-agent")

@mcp.tool()
def get_asset_price_data(ticker: str, start: str, end: str):
    """Get assets' price pandas DataFrame"""
    res = get_res_data(ticker, start, end)
    return clean_df(res)

@mcp.tool()
def plot_chart(ticker: str, start: str, end: str):
    """Get Assets/ price chart"""
    return plot_line_chart(ticker, start, end)

@mcp.tool()
def get_stock_metrics(ticker: str, start: str, end: str):
    """计算 Sharpe、波动率、回撤、收益率等"""
    return get_metrics(ticker, start, end)

# ③ 更新策略参数（不能用 **kwargs，必须显式列出字段）
@mcp.tool()
def update_params(
    indicator: str = "",
    buy_rule: str = "",
    sell_rule: str = "",
    ticker: str = "",
    start: str = "",
    end: str = ""
):
    """更新当前策略配置参数"""
    args = {k: v for k, v in locals().items() if v}
    return update_strategy_params(**args)

# ④ 回测工具
@mcp.tool()
def run_strategy_backtest():
    """使用内存中的当前策略参数运行回测"""
    return run_backtest(memory["strategy"])

# 启动 MCP 服务器
if __name__ == "__main__":
    mcp.run("stdio")
