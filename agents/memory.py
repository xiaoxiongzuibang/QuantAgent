# memory.py
memory = {
    "strategy": {k: None for k in ("indicator","buy_rule","sell_rule","ticker","start","end")},
    "cache": {}
}

def update_strategy_params(**kwargs) -> dict:
    memory["strategy"].update({k: v for k, v in kwargs.items() if v is not None})
    missing = [k for k, v in memory["strategy"].items() if v is None]
    return {"missing": missing}