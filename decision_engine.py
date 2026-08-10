# decision_engine.py (extracto de método evaluate)
def evaluate(self, symbol: str, df: pd.DataFrame) -> Dict:
    # ... (código existente)
    # Al final, asegurar que se incluyen estos campos:
    decision = {
        'action': action,  # 'BUY', 'SELL', 'HOLD'
        'symbol': symbol,
        'entry': last_price,
        'sl_pct': sl_pct,
        'tp_pct': tp_pct,
        'edge_data': edge_data,
        'regime': regime,          # <--- AGREGAR
        'volatility': volatility,  # <--- AGREGAR
        'atr': atr,
        'adx': adx,
        'timestamp': datetime.now()
    }
    return decision
