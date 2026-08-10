# utils.py
import pandas as pd
from datetime import datetime, timedelta

def format_price(value: float) -> str:
    return f"${value:,.2f}"

def format_currency(value: float) -> str:
    return f"${value:,.2f}"

def format_pct(value: float) -> str:
    return f"{value*100:.2f}%"

def get_timeframe_minutes(tf: str) -> int:
    """Convierte timeframe a minutos."""
    if tf.endswith('m'):
        return int(tf[:-1])
    elif tf.endswith('h'):
        return int(tf[:-1]) * 60
    elif tf.endswith('D'):
        return int(tf[:-1]) * 1440
    return 5

def align_timeframes(dfs: dict) -> dict:
    """Alinea los índices de múltiples DataFrames."""
    common_idx = None
    for df in dfs.values():
        if df is not None and not df.empty:
            if common_idx is None:
                common_idx = df.index
            else:
                common_idx = common_idx.intersection(df.index)
    if common_idx is None:
        return {}
    return {tf: df.loc[common_idx] for tf, df in dfs.items() if df is not None and not df.empty}