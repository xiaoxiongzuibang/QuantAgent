# mcp_servers/market_data/server.py
from typing import Optional, Dict, Any
from fastmcp import FastMCP
from agent_core.data import *
from agent_core.plot import *
from agent_core.strategy import *
from agent_core.backtest import *
from agent_core.memory import *
from agent_core.dyn_loader import register_dynamic_strategy
from agent_core.backtest_bt import run_bt_backtest

mcp = FastMCP("quant-agent")

@mcp.tool()
def get_asset_price_data(ticker: str, start: str, end: str):
    """Get assets' price pandas DataFrame"""
    res = get_res_data(ticker, start, end)
    return clean_df(res)


@mcp.tool()
def get_stock_metrics(ticker: str, start: str, end: str):
    """计算 Sharpe、波动率、回撤、收益率等"""
    return get_metrics(ticker, start, end)

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

@mcp.tool()
def trend_backtest(ticker: str, start: str, end: str,
                   fast: int = 20, slow: int = 100, fee: float = 0.0005):
    """
    趋势跟踪回测：返回 stats + 图片
    """
    res = run_trend_backtest(ticker, start, end, fast, slow, fee)
    img = plot_equity_signals(res, ticker)
    res["image"] = img
    return res

@mcp.tool()
def create_strategy(name: str, code: str):
    """
    动态创建 Backtrader 策略
    """
    try:
        msg = register_dynamic_strategy(name, code)
        return {"status": "success", "msg": msg}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

@mcp.tool()
def backtest_strategy(
    ticker: str,
    start: str,
    end: str,
    method: str = "sma",
    cash: float = 100_000,
    params: Optional[Dict[str, Any]] = None   # ← 显式声明
):
    """
    通用 Backtrader 回测：params 里放策略超参
    """
    if params is None:
        params = {}
    return run_bt_backtest(ticker, start, end, method, cash, **params)

if __name__ == "__main__":
    mcp.run("stdio")
