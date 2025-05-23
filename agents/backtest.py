import backtrader as bt, matplotlib.pyplot as plt, uuid
from .data import *
from mycerebro import MyCerebro

def make_bt_strategy(cfg):
    class DynStrat(bt.Strategy):
        def __init__(self):
            ind = cfg["indicator"].lower()
            if ind in ("sma","ema"):
                cls = bt.ind.SMA if ind=="sma" else bt.ind.EMA
                self.fast = cls(period=5)
                self.slow = cls(period=20)
            elif ind == "rsi":
                self.rsi = bt.ind.RSI(period=14)
            elif ind == "macd":
                self.macd = bt.ind.MACD()
        def next(self):
            if not self.position and (_buy(cfg,self)):
                self.buy()
            elif self.position and (_sell(cfg,self)):
                self.close()
    return DynStrat

def _buy(c, s):
    return ((hasattr(s,"fast") and s.fast[0]>s.slow[0] and s.fast[-1]<=s.slow[-1])
            or (hasattr(s,"rsi") and s.rsi[0]<30)
            or (hasattr(s,"macd") and s.macd.macd[0]>s.macd.signal[0]))

def _sell(c, s):
    return ((hasattr(s,"fast") and s.fast[0]<s.slow[0] and s.fast[-1]>=s.slow[-1])
            or (hasattr(s,"rsi") and s.rsi[0]>70)
            or (hasattr(s,"macd") and s.macd.macd[0]<s.macd.signal[0]))

def run_backtest(cfg: dict) -> dict:
    today = dt.date.today().strftime("%Y-%m-%d")
    raw = yf.download(cfg["ticker"], cfg["start"], min(cfg["end"], today), auto_adjust=False, progress=False)
    if raw.empty:
        return {"error": "no data"}
    try:
        data = clean_df(raw)
    except ValueError as e:
        return {"error": str(e)}
    cerebro = MyCerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=data))
    cerebro.addstrategy(make_bt_strategy(cfg))
    cerebro.broker.setcash(100000)
    cerebro.run()
    fig = cerebro.plot(style='candlestick')[0][0]
    img = f"bt_{uuid.uuid4().hex[:8]}.png"
    fig.savefig(img, dpi=150, bbox_inches='tight')
    plt.close(fig)
    equity = cerebro.broker.getvalue()
    return {
        "summary": f"Final equity ${equity:,.2f} (PnL ${equity-100000:,.2f})",
        "image": img
    }