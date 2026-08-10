# trailing_engine.py
from indicators import Indicators

class TrailingEngine:
    """Trailing Stop adaptativo basado en condiciones de mercado."""

    @staticmethod
    def compute(entry_price: float, atr: float, adx: float, volatility: float,
                regime: str, be_trigger: float) -> Dict:
        """Calcula distancia de trailing stop óptima."""

        # Base: 1% del ATR
        base_distance = atr / entry_price * 0.8

        # Ajuste por ADX (tendencia fuerte = trailing más amplio)
        adx_factor = 1 + (adx - 25) / 50 * 0.3
        adx_factor = max(0.7, min(1.3, adx_factor))

        # Ajuste por volatilidad (mayor volatilidad = trailing más amplio)
        vol_factor = 1 + (volatility - 15) / 50 * 0.2
        vol_factor = max(0.8, min(1.2, vol_factor))

        # Ajuste por régimen
        regime_factors = {
            'Expansión': 1.3,
            'Tendencia Fuerte': 1.2,
            'Tendencia': 1.0,
            'Normal': 0.9,
            'Chop': 0.6
        }
        regime_factor = regime_factors.get(regime, 1.0)

        # Distancia final
        distance = base_distance * adx_factor * vol_factor * regime_factor
        distance = max(0.002, min(0.025, distance))

        # Activación: basada en Break Even + 1/3 de distancia
        activation = be_trigger + distance * 0.33
        activation = max(0.004, min(0.025, activation))

        return {
            'distance': distance,
            'activation': activation,
            'sl_price': entry_price * (1 - distance),
            'activation_price': entry_price * (1 + activation),
            'adx_factor': adx_factor,
            'vol_factor': vol_factor,
            'regime_factor': regime_factor
        }