from .data import *
import uuid
from .memory import memory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_line_chart(ticker: str, start: str, end: str) -> dict:
    try:
        df = get_cleaned_data(ticker, start, end)
    except Exception as e:
        return {"error": str(e)}
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