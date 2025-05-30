from typing import Optional, Dict, Any
from fastmcp import FastMCP
import pandas as pd

from agent_core.data.price_data import *
from agent_core.data.fundamental_data import *
from agent_core.data.macro_data import *

from agent_core.factors.tech_factors import *
from agent_core.factors.fundamental_factors import *

from agent_core.strategy.strategy_builder import *
from agent_core.backtest.factor_backtest import *

from agent_core.factors.factor_registry import *

df = yf.download("TSLA", "2023-01-01", "2024-01-01")
# df = get_res_price_data("TSLA", "2023-01-01", "2024-01-01")
print(df.tail().to_dict())

  