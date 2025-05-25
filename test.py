# test_trend.py  放在项目根目录，运行 python test_trend.py
from agents.backtest import run_trend_backtest
from agents.plot import plot_equity_signals

res = run_trend_backtest("AAPL", "2023-01-01", "2024-01-01", fast=20, slow=100)
print(res["stats"])
img = plot_equity_signals(res, "AAPL")
print("Saved plot:", img)


