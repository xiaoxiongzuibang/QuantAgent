# verify_tools.py
from agents.data     import *
from agents.plot     import plot_line_chart
from agents.backtest import get_metrics, run_backtest

if __name__ == "__main__":
    print("=== get_asset_data ===")
    res = get_res_data("AAPL", "2023-01-01", "2023-12-31")
    print(clean_df(res))

    # print("\n=== plot_line_chart ===")
    # result = plot_line_chart("AAPL", "2023-01-01", "2023-12-31")
    # print(result)  # 应该是 {'image': 'line_xxxxx.png'}

    # print("\n=== get_metrics ===")
    # print(get_metrics("AAPL", "2023-01-01", "2023-12-31"))

    # 如果你想测试 run_backtest，请注意它会生成图片文件：
    # print("\n=== run_backtest ===")
    # print(run_backtest(memory["strategy"]))

