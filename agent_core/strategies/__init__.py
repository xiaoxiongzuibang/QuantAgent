import importlib, pkgutil, inspect, backtrader as bt

REGISTRY = {}                # 全局可写字典

def register(name: str):
    """装饰器：把 Strategy 子类放入 REGISTRY"""
    def deco(cls):
        if not issubclass(cls, bt.Strategy):
            raise TypeError("Must inherit bt.Strategy")
        REGISTRY[name] = cls
        return cls
    return deco

def _discover():
    pkg_path = __path__
    for _, modname, _ in pkgutil.iter_modules(pkg_path):
        if not modname.startswith("_"):
            importlib.import_module(f"{__name__}.{modname}")
_discover()    # 导入包时自动执行一次扫描
