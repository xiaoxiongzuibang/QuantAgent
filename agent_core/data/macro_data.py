from fredapi import Fred
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()


# 初始化 FRED 客户端
FRED_API_KEY = os.getenv("FRED_API_KEY")  # 建议存到 .env 文件
fred = Fred(api_key=FRED_API_KEY)

# 获取单个宏观指标数据
def get_macro_data(series_id: str, start: str = "2000-01-01", end: str = None) -> pd.DataFrame:
    df = fred.get_series(series_id, observation_start=start, observation_end=end)
    df = df.to_frame(name=series_id)
    df.index.name = "date"
    return df

# 示例常用指标
MACRO_SERIES = {
    "GDP": "GDP",  # 美国实际国内生产总值
    "CPI": "CPIAUCSL",  # 消费者价格指数
    "UNRATE": "UNRATE",  # 失业率
    "FEDFUNDS": "FEDFUNDS"  # 联邦基金利率
}

# 获取多个指标
def get_macro_dataset(indicators: list[str], start: str = "2000-01-01", end: str = None) -> pd.DataFrame:
    frames = [get_macro_data(MACRO_SERIES[ind], start, end) for ind in indicators]
    return pd.concat(frames, axis=1)
