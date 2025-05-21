import os, json, uuid, datetime as dt
import pandas as pd, numpy as np
import backtrader as bt, yfinance as yf, matplotlib.pyplot as plt
from openai import OpenAI
from mycerebro import MyCerebro
import matplotlib
matplotlib.use("Agg")  # ✅ 保证使用非 GUI 后端
import matplotlib.pyplot as plt

plt.show = lambda *args, **kwargs: None



# ---------- function_call ----------
functions = [
    {
        "name": "plot_stock_chart",
        "description": "Plot raw price chart for a stock in a given date range",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start":  {"type": "string"},
                "end":    {"type": "string"}
            },
            "required": ["ticker", "start", "end"]
        }
    },
    {
        "name": "update_strategy_params",
        "description": "Collect/update strategy parameters",
        "parameters": {
            "type": "object",
            "properties": {
                "indicator": {"type": "string"},
                "buy_rule":  {"type": "string"},
                "sell_rule": {"type": "string"},
                "ticker":    {"type": "string"},
                "start":     {"type": "string"},
                "end":       {"type": "string"}
            }
        }
    },
    {
        "name": "run_backtest",
        "description": "Run backtest, return summary & chart path",
        "parameters": {
            "type": "object",
            "properties": {"strategy": {"type": "object"}},
            "required": ["strategy"]
        }
    }
]

# ---------- Agent 记忆 ----------
memory = {"strategy": {k: None for k in
           ("indicator","buy_rule","sell_rule","ticker","start","end")}}

# ---------- 绘制资产价格图像 ----------
import uuid
import matplotlib.pyplot as plt

def plot_line_chart(ticker, start, end):
    try:
        df = get_cleaned_data(ticker, start, end)
    except Exception as e:
        return {"error": str(e)}

    plt.figure(figsize=(10, 4))
    plt.plot(df.index, df["close"], label=f"{ticker} Close Price", color="blue")
    plt.title(f"{ticker} Price ({start} to {end})")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.tight_layout()

    img_path = f"line_{uuid.uuid4().hex[:8]}.png"
    plt.savefig(img_path)
    plt.close()
    return {"image": img_path}


# ---------- Backtrader 动态策略 ----------
def make_bt_strategy(cfg):
    class DynStrat(bt.Strategy):
        def __init__(self):
            ind = cfg["indicator"].lower()
            if ind in {"sma","ema"}:
                cls = bt.ind.SMA if ind=="sma" else bt.ind.EMA
                self.fast, self.slow = cls(period=5), cls(period=20)
            elif ind=="rsi":
                self.rsi = bt.ind.RSI(period=14)
            elif ind=="macd":
                self.macd = bt.ind.MACD()

        def next(self):
            if not self.position and _buy(cfg,self): self.buy()
            elif self.position and _sell(cfg,self): self.close()
    return DynStrat

def _buy(c,s):  # 简版
    return (hasattr(s,"fast") and s.fast[0]>s.slow[0] and s.fast[-1]<=s.slow[-1]) \
        or (hasattr(s,"rsi") and s.rsi[0]<30) \
        or (hasattr(s,"macd") and s.macd.macd[0]>s.macd.signal[0])
def _sell(c,s):
    return (hasattr(s,"fast") and s.fast[0]<s.slow[0] and s.fast[-1]>=s.slow[-1]) \
        or (hasattr(s,"rsi") and s.rsi[0]>70) \
        or (hasattr(s,"macd") and s.macd.macd[0]<s.macd.signal[0])

# ---------- Data Module ----------
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns,pd.MultiIndex):
        df.columns=[t[0].replace(' ','').lower() for t in df.columns]
    else:
        df.columns=[c.lower() for c in df.columns]
    if "close" not in df.columns and "adjclose" in df.columns:
        df["close"]=df["adjclose"]
    need=["open","high","low","close","volume"]
    miss=[c for c in need if c not in df.columns]
    if miss: raise ValueError(f"missing cols {miss}")
    df=df[need].apply(pd.to_numeric,errors="coerce").ffill().dropna()
    df.replace([np.inf,-np.inf],np.nan,inplace=True); df.dropna(inplace=True)
    if len(df)<30: raise ValueError("bars<30")
    return df

def get_cleaned_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    从缓存中获取清洗过的数据，如果没有则调用 yfinance 下载 + clean_df()
    """
    key = f"{ticker}_{start}_{end}"
    if "cache" not in memory:
        memory["cache"] = {}

    if key not in memory["cache"]:
        df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
        if df.empty:
            raise ValueError("No data")
        df = clean_df(df)  # ✅ 调用你的底层函数
        memory["cache"][key] = df

    return memory["cache"][key]



def run_backtest(cfg):
    today = dt.date.today().strftime("%Y-%m-%d")
    raw = yf.download(cfg["ticker"], cfg["start"], min(cfg["end"],today),
                      auto_adjust=False, progress=False)
    if raw.empty: return {"error":"no data"}
    try:
        data = clean_df(raw)
    except ValueError as e:
        return {"error": str(e)}

    cerebro = MyCerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=data, openinterest=None))
    cerebro.addstrategy(make_bt_strategy(cfg))
    cerebro.broker.setcash(100_000)
    cerebro.run()


    fig = cerebro.plot(style='candlestick')[0][0]
    img = f"bt_{uuid.uuid4().hex[:8]}.png"
    fig.savefig(img, dpi=150, bbox_inches='tight')
    plt.close(fig)

    equity = cerebro.broker.getvalue()
    return {"summary": f"Final equity ${equity:,.2f} (PnL ${equity-100_000:,.2f})",
            "image": img}

def update_strategy_params(**kwargs):
    """
    接收来自 GPT 函数调用的参数，更新到 memory['strategy']。
    返回缺失字段列表，便于 GPT 再次提问。
    """
    memory["strategy"].update({k: v for k, v in kwargs.items() if v})
    missing = [k for k, v in memory["strategy"].items() if v is None]
    return {"missing": missing}

# ---------- OpenAI API ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt(msgs: list) -> str:
    return client.chat.completions.create(
        model="gpt-4o",
        messages=msgs,
        functions=functions,
        function_call="auto"
    ).choices[0].message


if __name__ == "__main__":

    msgs=[{"role":"system","content":"You are a quant trading assistant."}]
    print("Hi！我是精通量化交易的Agent! 我能呢帮你什么？（输入exit以退出聊天）")
    while True:
        user_input=input("User: "); 
        if user_input.lower() in {"exit","quit"}: break
        msgs.append({"role":"user","content":user_input})

        assistant=gpt(msgs); msgs.append(assistant)

        while assistant.function_call:
            function_name=assistant.function_call.name
            args=json.loads(assistant.function_call.arguments or "{}")

            if function_name=="update_strategy_params":
                memory["strategy"].update({k:v for k,v in args.items() if v})
                miss=[k for k,v in memory["strategy"].items() if v is None]
                msgs.append({"role":"function","name":function_name,
                            "content":"params ok" if not miss else f"still need {miss}"})

            elif function_name=="run_backtest":
                res=run_backtest(memory["strategy"])
                if "error" in res:
                    msgs.append({"role":"function","name":function_name,"content":res["error"]})
                else:
                    # ① 把摘要给 GPT 生成自然语言
                    msgs.append({"role":"function","name":function_name,"content":res["summary"]})
                    print(f"图表已保存为 {res['image']}")   # ② 本地提示图路径

            assistant=gpt(msgs); msgs.append(assistant)

        print("Agent: ", assistant.content)
    
