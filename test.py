from agent_core.price_data import *
from agent_core.fundamental_data import *

# tsla_fun =  get_fundamentals(["AAPL"])
# print(tsla_fun.info)

df = get_res_data(["TSLA","AAPL"], "2023-01-01", "2024-01-01")
print(df)
  