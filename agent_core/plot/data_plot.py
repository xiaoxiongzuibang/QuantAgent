import matplotlib.pyplot as plt
from agent_core.data.price_data import *
from agent_core.data.fundamental_data import *
from agent_core.data.macro_data import *
import uuid

def plot_res_line_chart(ticker: str, start: str, end: str, df: pd.DataFrame) -> dict:
    plt.figure(figsize=(10,4))
    plt.plot(df.index, df["close"], label=f"{ticker} Close Price")
    plt.title(f"{ticker} Price from {start} to {end}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.tight_layout()
    path = f"line_{uuid.uuid4().hex[:8]}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return {"image": path}

def plot_2d_line_chart(title: str, x_label: str, y_label:str, x_data, y_data, width:10, height:4):
    plt.figure(figsize=(width,height))
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)

def plot_2d_scatter_chart():
    ...