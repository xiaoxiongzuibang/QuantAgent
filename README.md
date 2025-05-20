# 💹 Quant Strategy GPT Agent (Gradio Edition)

This project allows users to describe quantitative trading strategies in natural language (like "MACD crossover on AAPL since 2022"), run a backtest with Backtrader, and view the results interactively using a web UI powered by Gradio.

---

## 📦 Features

- 💬 ChatGPT-style interface — describe your strategy in plain English or Chinese
- 🤖 OpenAI Function Calling automatically fills in strategy parameters
- 📈 Backtesting engine built with [Backtrader](https://www.backtrader.com/)
- 🖼️ Automatically generated strategy charts
- 🌐 Zero frontend development — everything runs via Python and Gradio

---

## 🗂️ Project Structure
```
QuantAgent/
├── strategy_agent.py # Core logic: GPT, parameter memory, backtesting
├── gradio_app.py # Gradio chat interface
├── .env # API key file (you can create this)
├── requirements.txt # Python dependencies
├── bt_*.png # Auto-generated backtest charts
└── README.md # This fil
```

## ⚙️ Getting Started

### ✅ Step 1. Clone the repository

```bash
git clone https://github.com/your-username/QuantAgent.git
```
### ✅ Step 2. Create a virtual environment (recommended)
```bash
cd QuantAgent
python -m venv venv
source venv/bin/activate          # macOS / Linux
# .\venv\Scripts\activate         # Windows
```
### ✅ Step 3. Install dependencies
```bash
pip install -r requirements.txt
```
### ✅ Step 4. Set your OpenAI API
```bash
# Option A: Set it as an environment variable
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Option B (recommended): Create a .env file
echo "OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
```
### ✅ Step 5. Start up
```bash
python gradio_app.py
# open your browsers and go to http://127.0.0.1:7860
```


