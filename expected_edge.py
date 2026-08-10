# expected_edge.py (CORREGIDO)
import numpy as np
from typing import Dict, Optional

class ExpectedEdge:
    """Expected Edge Score basado en rentabilidad esperada con datos históricos."""
    
    @staticmethod
    def compute(score: float, adx: float, ker: float, atr_pct: float, 
                regime: str, win_rate: float = 0.55, pf: float = 1.2,
                tp_pct: float = 1.0, sl_pct: float = 0.5,
                avg_duration: Optional[float] = None, 
                trades_per_day: Optional[float] = None) -> Dict:
        """
        Calcula el Expected Edge y todas las métricas asociadas.
        
        Args:
            score: PiDelta Score
            adx: ADX
            ker: Kaufman Efficiency Ratio
            atr_pct: ATR como porcentaje
            regime: Régimen de mercado
            win_rate: Win Rate histórico
            pf: Profit Factor histórico
            tp_pct: Take Profit en porcentaje
            sl_pct: Stop Loss en porcentaje
            avg_duration: Duración promedio de trades (horas) - opcional
            trades_per_day: Trades por día - opcional
        """
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
        
        # Si no se proporcionan avg_duration y trades_per_day, usar valores estimados
        if avg_duration is None:
            # Estimar basado en ATR y volatilidad
            avg_duration = 1.5 + (atr_pct * 50)  # Mayor volatilidad = mayor duración
            avg_duration = max(0.5, min(6.0, avg_duration))  # Entre 0.5 y 6 horas
        
        if trades_per_day is None:
            # Estimar basado en win_rate y volatilidad
            trades_per_day = 0.5 + (win_rate * 1.5)  # Mayor win rate = más trades
            trades_per_day = max(0.2, min(5.0, trades_per_day))  # Entre 0.2 y 5
        
        # Métricas derivadas
        expected_pnl_per_trade = edge * 100  # %
        expected_pnl_per_hour = expected_pnl_per_trade / avg_duration if avg_duration > 0 else 0
        expected_pnl_daily = expected_pnl_per_trade * trades_per_day
        
        # Risk of Ruin (Kelly)
        if pf > 0:
            kelly = win_rate - (1 - win_rate) / pf if pf > 0 else 0
            kelly = max(0, min(1, kelly))
            risk_of_ruin = np.exp(-2 * kelly * (0.015 / max(kelly, 0.001))) if kelly > 0 else 1.0
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
            'regime_factor': regime_factor,
            'avg_duration_used': avg_duration,
            'trades_per_day_used': trades_per_day
        }
