# QuantAgent: A Claude-Compatible Factor Investing Framework

## 🧠 Motivation: Mathematical Foundations of Factor Investing

Factor investing is grounded in financial economics and inspired by models like the Arbitrage Pricing Theory (APT), which suggests that asset returns can be approximated as a linear combination of a small number of systematic risk factors.

In modern quantitative finance, each factor is treated as a stochastic process — a time-varying random variable sequence. These processes represent evolving economic forces like value, momentum, quality, and size.

This project leverages these ideas to build a programmable framework for factor construction, evaluation, and backtesting using Claude-compatible AI interfaces.

---

## 📁 Project Structure

```
QuantAgent/
├── agent_core
│   ├── __init__.py
│   ├── backtest
│   │   └── factor_backtest.py
│   ├── data
│   │   ├── __init__.py
│   │   ├── fundamental_data.py
│   │   ├── macro_data.py
│   │   └── price_data.py
│   ├── factors
│   │   ├── __init__.py
│   │   ├── fundamental_factors.py
│   │   └── tech_factors.py
│   └── plot
│       ├── __init__.py
│       ├── backtest_plot.py
│       └── data_plot.py
├── chat.py       # run for using OpenAI CLI
├── server.py     # run for using Claude Desktop or Cline
├── mycerebro.py
├── openai_agent
│   ├── __init__.py
│   └── functions.py
├── pyproject.toml
├── README.md
```

---

## 🚀 Quickstart: CLI Demonstration

```bash
# Create virtual environment
conda create -n mcp_env python=3.10 -y
conda activate mcp_env

git clone https://github.com/xiaoxiongzuibang/QuantAgent.git
cd QuantAgent

# Install dependencies
pip install -e ".[dev]"
```

---

## 🤖 Claude Integration: MCP Configuration Example

To use this project as a Claude-compatible agent via FastMCP, you need to edit your Claude Desktop configuration file (usually located at `~/.claude_desktop_config.json`) like this:

```json
{
  "mcpAgentServers": [
    {
      "id": "quant-agent",
      "command": "/opt/anaconda3/envs/mcp_env/bin/python",
      "args": [
        "/Users/yourname/Desktop/Project/QuantAgent/mcp_servers/market_data/server.py"
      ]
    }
  ],
  "mcpServers": {
    "quantAgent": {
      "command": "/opt/anaconda3/envs/mcp_env/bin/python",
      "args": [
        "/Users/yourname/Desktop/Project/QuantAgent/mcp_servers/market_data/server.py"
      ]
    }
  }
}
```

### Notes:
- `command` is the absolute path to your Python interpreter (usually inside the Conda environment you created).
- `args[0]` must be the **absolute path** to your agent script (`server.py`). You can find this by running `pwd` inside the project folder.
- Make sure `server.py` is the entry point script that launches your `FastMCP(...).run("stdio")` server.

Once configured, you can restart Claude Desktop and Claude will automatically load this agent when needed.

---

## 🤖 Using the OpenAI CLI to Run the Factor Investment Agent

You can interact with this project's `chat.py` script using OpenAI's Function Calling via the command-line interface (CLI).
You can get your OpenAI API keys on its website(usually like "sk-xxxxx").

Make sure the OpenAI CLI is installed:

```bash
pip install openai

# Set Up Your API Key and add your OpenAI API key to a .env file in the project root:
echo "OPENAI_API_KEY=sk-xxxxx..." >> .env

# Alternatively, export it directly in the terminal (not recommended for long-term use):
export OPENAI_API_KEY="sk-xxxxx..."

python chat.py # run for using OpenAI CLI
```

## 🧪 Example Use Cases in Claude or OpenAI

Once the agent is connected, you can interact naturally:

- "Download the price data of META form 2023-01-01 to 2024-01-01"
- "Give me the fundamental data of tesla related to income sheet during 2023"
- "Compute RSI for TSLA"
- "Use ROE to build a factor and test if it correlates with future return"
- "Which stocks among AAPL, TSLA, NVDA have highest dividend yield?"

Claude will internally call tools such as:
- `download_prices`
- `get_fundamentals`
- `compute_rsi`
- `compute_roe`
- `simple_backtest`

---

## 📬 Contributions

Feel free to open issues, submit pull requests, or ask questions. This project is aimed at educational and experimental usage of factor investing using AI agents.

---

## 📘 References

- Cochrane, J. H. (2005). *Asset Pricing*.
- Fama, E. & French, K. (1993). *Common risk factors in the returns on stocks and bonds*.
- Harvey, Liu & Zhu (2015). *…and the Cross-Section of Expected Returns*.