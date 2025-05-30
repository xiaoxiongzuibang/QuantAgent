import pandas as pd

def generate_top_n_signal(factor_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    根据因子值，选出每个日期中前 top_n 的股票，返回 signal DataFrame，1表示持仓，0表示空仓。
    输入：index 为日期，columns 为股票代码的因子值 DataFrame
    """
    signal = factor_df.rank(axis=1, ascending=False) <= top_n
    return signal.astype(int)

def generate_last_n_signal(factor_df: pd.DataFrame, last_n: int = 10) -> pd.DataFrame:
    """
    根据因子值，选出每个日期中后 last_n 的股票，返回 signal DataFrame，1表示持仓，0表示空仓。
    输入：index 为日期，columns 为股票代码的因子值 DataFrame
    """
    signal = factor_df.rank(axis=1, ascending=True) <= last_n
    return signal.astype(int)

def equal_weight(signal_df: pd.DataFrame) -> pd.DataFrame:
    """
    根据 signal 生成等权重组合，未选中股票权重为0，选中股票均分权重
    """
    weight_df = signal_df.div(signal_df.sum(axis=1), axis=0).fillna(0)
    return weight_df
