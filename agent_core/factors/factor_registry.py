import pandas as pd
from agent_core.factors.tech_factors import *

# 函数字典：内部使用的标准名称 → 对应的函数
FACTOR_FUNCTIONS = {
    "momentum": calc_momentum,
    "volatility": calc_volatility,
}

# 自然语言 → 标准函数名（兼容 LLM 输入）
FACTOR_REGISTRY = {
    "动量因子": "momentum",
    "momentum": "momentum",
    "momentum factor": "momentum",
    "动量": "momentum",

    "波动率因子": "volatility",
    "volatility": "volatility",
    "volatility factor": "volatility",
    "低波动": "volatility",
}

# 主调用函数：根据用户输入获取计算后的因子 DataFrame
def get_factor(factor_name: str, price_df) -> 'pd.DataFrame':
    name_clean = factor_name.strip().lower()  # ← 去除前后空格并小写
    key = FACTOR_REGISTRY.get(name_clean)
    if not key:
        raise ValueError(f"❌ 未知因子名称：{repr(factor_name)}")
    func = FACTOR_FUNCTIONS[key]
    return func(price_df)
