# trailing_engine.py
import numpy as np
from typing import Dict

class TrailingEngine:
    """Calcula el Trailing Stop dinámico basado en ATR, ADX y régimen."""
    
    @staticmethod
    def compute(entry_price: float, atr: float, adx: float, volatility: float, 
                regime: str, be_trigger: float) -> Dict:
        atr_pct = atr / entry_price if entry_price > 0 else 0.01
        regime_factors = {
            'Expansión': 1.5,
            'Tendencia Fuerte': 1.3,
            'Tendencia': 1.0,
            'Normal': 0.8,
            'Chop': 0.5
        }
        regime_factor = regime_factors.get(regime, 1.0)
        adx_factor = 0.5 + 0.5 * min(adx / 40.0, 1.0)
        base_distance = atr_pct * 1.5
        distance = base_distance * regime_factor * (1 / adx_factor)
        distance = max(0.005, min(0.05, distance))
        activation = distance * 1.5
        callback = distance * 0.3
        return {
            'distance': distance,
            'activation': activation,
            'callback': callback,
            'atr_pct': atr_pct,
            'regime_factor': regime_factor,
            'adx_factor': adx_factor
        }
