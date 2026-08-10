# expected_edge.py
import numpy as np

class ExpectedEdge:
    """Expected Edge Score basado en rentabilidad esperada."""

    @staticmethod
    def compute(score, adx, ker, atr_pct, regime, win_rate=0.55, pf=1.2, tp_pct=1.0, sl_pct=0.5):
        """Calcula el Expected Edge y todas las métricas asociadas."""

        # Factores de régimen
        regime_factors = {
            'Expansión': 1.2,
            'Tendencia Fuerte': 1.1,
            'Tendencia': 1.0,
            'Normal': 0.8,
            'Chop': 0.3
        }
        regime_factor = regime_factors.get(regime, 0.8)

        # Edge base
        avg_win = tp_pct / 100
        avg_loss = sl_pct / 100
        edge = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

        # Ajustes
        confidence = abs(score)
        edge *= (0.5 + 0.5 * confidence)
        edge *= regime_factor
        edge *= (0.5 + 0.5 * ker)

        # Métricas derivadas
        expected_pnl_per_trade = edge * 100  # %
        avg_duration = 2.1  # horas
        expected_pnl_per_hour = expected_pnl_per_trade / avg_duration
        trades_per_day = 1.2
        expected_pnl_daily = expected_pnl_per_trade * trades_per_day

        # Risk of Ruin (Kelly)
        if pf > 0:
            kelly = win_rate - (1 - win_rate) / pf
            kelly = max(0, min(1, kelly))
            risk_of_ruin = np.exp(-2 * kelly * (0.015 / kelly)) if kelly > 0 else 1.0
        else:
            risk_of_ruin = 1.0

        # Clasificación
        if edge > 0.70:
            classification = 'Ventaja Ω'
            label = 'Ω'
        elif edge > 0.50:
            classification = 'Alta ventaja'
            label = 'A'
        elif edge > 0.30:
            classification = 'Ventaja media'
            label = 'M'
        elif edge > 0.10:
            classification = 'Baja ventaja'
            label = 'B'
        else:
            classification = 'Evitar'
            label = 'E'

        return {
            'expected_edge': edge,
            'expected_edge_pct': edge * 100,
            'expected_pnl_per_trade': expected_pnl_per_trade,
            'expected_pnl_per_hour': expected_pnl_per_hour,
            'expected_pnl_per_hour_usd': expected_pnl_per_hour / 100 * 10000,
            'expected_pnl_daily': expected_pnl_daily,
            'expected_pnl_daily_usd': expected_pnl_daily / 100 * 10000,
            'win_rate': win_rate,
            'profit_factor': pf,
            'risk_of_ruin': risk_of_ruin,
            'classification': classification,
            'label': label,
            'confidence': confidence,
            'regime_factor': regime_factor
        }
