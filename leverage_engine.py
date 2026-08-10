# leverage_engine.py
import numpy as np

class LeverageEngine:
    """Calcula apalancamiento óptimo basado en estadísticas históricas."""

    @staticmethod
    def compute(volatility: float, win_rate: float, profit_factor: float,
                max_drawdown: float, confidence: float) -> Dict:
        """Retorna apalancamiento recomendado, máximo y seguro."""
        if volatility <= 0:
            return {'recommended': 1, 'max': 3, 'safe': 1}

        # Kelly fraccional
        kelly = win_rate - (1 - win_rate) / profit_factor if profit_factor > 0 else 0
        kelly = max(0, min(1, kelly))

        # Factor de volatilidad
        vol_factor = 0.5 / volatility  # si ATR=1%, factor=50; si ATR=2%, factor=25

        # Confianza
        conf_factor = 0.5 + 0.5 * confidence

        # Drawdown limit
        dd_factor = 1 - min(max_drawdown / 0.20, 0.5)

        # Apalancamiento base
        base = kelly * 20 * conf_factor * dd_factor

        # Ajuste por volatilidad
        leveraged = base * (vol_factor / 10)

        # Recomendado (redondeado)
        recommended = max(1, min(12, int(round(leveraged))))

        # Máximo seguro (2x recomendado)
        max_safe = min(20, recommended * 2)

        # Máximo absoluto
        max_abs = min(30, max_safe * 1.5)

        return {
            'recommended': recommended,
            'max_safe': max_safe,
            'max_absolute': max_abs,
            'kelly': kelly,
            'volatility_factor': vol_factor,
            'confidence_factor': conf_factor,
            'dd_factor': dd_factor
        }
