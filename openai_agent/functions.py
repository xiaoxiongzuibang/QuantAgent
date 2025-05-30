
function_schemas = [
    # =====data module=====
    {
        "name": "get_res_price_data",
        "description": "Get OHLCV price data for one or more tickers over a time range.",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of stock ticker symbols, e.g., ['AAPL', 'TSLA']"
                },
                "start": {"type": "string", "description": "Start date, e.g., '2023-01-01'"},
                "end": {"type": "string", "description": "End date, e.g., '2024-01-01'"}
            },
            "required": ["tickers", "start", "end"]
        }
    },
    {
        "name": "get_fundamental_data",
        "description": "Fetch recent annual and TTM fundamental indicators (balance sheet, income, cash flow, ratios).",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of stock ticker symbols"
                }
            },
            "required": ["tickers"]
        }
    },
    {
        "name": "get_macro_data",
        "description": "Get a macroeconomic time series indicator (e.g., CPI, GDP, interest rates).",
        "parameters": {
            "type": "object",
            "properties": {
                "indicator": {
                    "type": "string",
                    "description": "Macroeconomic indicator symbol, e.g., 'CPIAUCNS' for US CPI."
                },
                "start": {"type": "string"},
                "end": {"type": "string"}
            },
            "required": ["indicator", "start", "end"]
        }
    },
    {
        "name": "plot_res_line_chart",
        "description": "Plot a stock price line chart using supplied OHLCV data.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start":  {"type": "string"},
                "end":    {"type": "string"},
                "df": {
                    "type": "array",
                    "description": "List of rows with 'date' and 'close' for plotting.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "close": {"type": "number"}
                        },
                        "required": ["date", "close"]
                    }
                }
            },
            "required": ["ticker", "start", "end", "df"]
        }
    },
    {
        "name": "macro_data",
        "description": "Get macroeconomic time series such as GDP, CPI, or unemployment rate.",
        "parameters": {
            "type": "object",
            "properties": {
            "indicators": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of macro indicators (e.g., 'GDP', 'CPI', 'UNRATE')"
            },
            "start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
            "end": {"type": "string", "description": "End date (YYYY-MM-DD)"}
            },
            "required": ["indicators"]
        }
    }

]
