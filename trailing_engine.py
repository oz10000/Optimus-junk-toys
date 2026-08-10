# trailing_engine.py
import numpy as np
from typing import Dict

class TrailingEngine:
    """Calcula el Trailing Stop dinámico basado en ATR, ADX y régimen."""
    
    @staticmethod
    def compute(entry_price: float, atr: float, adx: float, volatility: float, 
                regime: str, be_trigger: float) -> Dict:
        """
        Calcula los parámetros del Trailing Stop.
        
        Args:
            entry_price: Precio de entrada
            atr: Average True Range
            adx: Average Directional Index
            volatility: Volatilidad actual
            regime: Régimen de mercado ('Expansión', 'Tendencia Fuerte', etc.)
            be_trigger: Trigger de Break Even (para ajuste)
        
        Returns:
            Dict con distance, activation, callback
        """
        # ATR como porcentaje del precio
        atr_pct = atr / entry_price if entry_price > 0 else 0.01
        
        # Factor base según régimen
        regime_factors = {
            'Expansión': 1.5,
            'Tendencia Fuerte': 1.3,
            'Tendencia': 1.0,
            'Normal': 0.8,
            'Chop': 0.5
        }
        regime_factor = regime_factors.get(regime, 1.0)
        
        # Ajuste por ADX (mayor ADX = tendencia más fuerte = trailing más agresivo)
        adx_factor = 0.5 + 0.5 * min(adx / 40.0, 1.0)
        
        # Distancia del trailing stop (en porcentaje)
        # Base: 1.5x ATR, ajustado por régimen y ADX
        base_distance = atr_pct * 1.5
        distance = base_distance * regime_factor * (1 / adx_factor)
        distance = max(0.005, min(0.05, distance))  # Entre 0.5% y 5%
        
        # Activación: distancia * 1.5 (se activa cuando el precio ha subido suficiente)
        activation = distance * 1.5
        
        # Callback: distancia * 0.3 (para trailing step)
        callback = distance * 0.3
        
        return {
            'distance': distance,
            'activation': activation,
            'callback': callback,
            'atr_pct': atr_pct,
            'regime_factor': regime_factor,
            'adx_factor': adx_factor
        }
