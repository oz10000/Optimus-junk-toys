# break_even_engine.py
import numpy as np
from indicators import Indicators

class BreakEvenEngine:
    """Motor de Break Even con enfoques técnico y estadístico."""

    @staticmethod
    def technical(entry_price: float, atr: float, volatility: float) -> Dict:
        """Break Even técnico basado en ATR y volatilidad."""
        # Distancia mínima para cubrir comisiones y slippage
        min_be = 0.0004 + 0.0005  # 0.04% + 0.05%
        # Ajuste por ATR
        atr_be = atr / entry_price * 0.15  # 15% del ATR
        # Ajuste por volatilidad
        vol_be = volatility / 100 * 0.2
        trigger = max(min_be, atr_be + vol_be)
        trigger = min(trigger, 0.015)  # máximo 1.5%
        return {
            'trigger': trigger,
            'price': entry_price * (1 + trigger),
            'method': 'technical',
            'type': 'ATR + Volatilidad'
        }

    @staticmethod
    def statistical(entry_price: float, history: list) -> Dict:
        """Break Even estadístico basado en histórico de trades."""
        if not history or len(history) < 10:
            return {'trigger': 0.004, 'price': entry_price * 1.004, 'method': 'statistical', 'type': 'default'}

        # Calcular el punto donde el trade ya pagó comisiones y spread
        pnls = [t.get('pnl_pct', 0) for t in history if t.get('pnl_pct', 0) > 0]
        if not pnls:
            return {'trigger': 0.004, 'price': entry_price * 1.004, 'method': 'statistical', 'type': 'default'}

        # Percentil 25 de las ganancias: punto donde el 25% de los trades ya cubrieron costos
        trigger = np.percentile(pnls, 25) / 100
        trigger = max(0.002, min(0.015, trigger))
        return {
            'trigger': trigger,
            'price': entry_price * (1 + trigger),
            'method': 'statistical',
            'type': f'percentil 25 de {len(pnls)} ganancias'
        }

    @staticmethod
    def select_best(entry_price: float, atr: float, volatility: float, history: list) -> Dict:
        """Compara ambos métodos y elige el mejor."""
        tech = BreakEvenEngine.technical(entry_price, atr, volatility)
        stat = BreakEvenEngine.statistical(entry_price, history)

        # Elegir el trigger más conservador (el que protege antes)
        if tech['trigger'] < stat['trigger']:
            tech['selected'] = True
            tech['reason'] = 'técnico más conservador'
            return tech
        else:
            stat['selected'] = True
            stat['reason'] = 'estadístico más adaptado al histórico'
            return stat