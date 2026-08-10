# signal_generator.py
from typing import Dict, Optional
from datetime import datetime


class SignalGenerator:
    """
    Genera señales formateadas a partir de decisiones del DecisionEngine.
    """

    @staticmethod
    def generate(decision: Dict) -> Optional[Dict]:
        """
        Convierte una decisión en señal completa.
        Retorna None si la decisión es inválida o es HOLD.
        """
        if decision is None:
            return None

        # Si es HOLD o NEUTRAL, no generar señal
        action = decision.get('action', 'HOLD')
        direction = decision.get('direction', 'NEUTRAL')
        if action == 'HOLD' or direction == 'NEUTRAL':
            return None

        # Extraer datos
        edge_data = decision.get('edge_data', {})
        next_est = decision.get('next_trade_est', {})

        # Calcular TP price correctamente
        entry = decision.get('entry_price', 0)
        tp_pct = decision.get('tp_pct', 0.04)
        if direction == 'LONG':
            tp_price = entry * (1 + tp_pct)
        else:
            tp_price = entry * (1 - tp_pct)

        return {
            # ===== IDENTIFICACIÓN =====
            'symbol': decision.get('symbol', 'unknown'),
            'direction': direction,
            'timestamp': decision.get('timestamp', datetime.now()),

            # ===== PRECIOS =====
            'entry': entry,
            'sl': decision.get('sl_price', 0),
            'tp': tp_price,
            'sl_pct': decision.get('sl_pct', 0.02),
            'tp_pct': decision.get('tp_pct', 0.04),

            # ===== SCORING =====
            'score': decision.get('score', 0),
            'adx': decision.get('adx', 0),
            'ker': decision.get('ker', 0),
            'regime': decision.get('regime', 'Normal'),
            'volatility': decision.get('volatility', 0),
            'pidelta': decision.get('pidelta', 0),
            'consensus_score': decision.get('consensus_score', 0),

            # ===== EXPECTED EDGE =====
            'edge': decision.get('edge', 0),
            'edge_pct': decision.get('edge_pct', 0),
            'classification': decision.get('classification', 'Evitar'),
            'label': decision.get('label', 'E'),
            'confidence': decision.get('confidence', 0.5),
            'win_rate': decision.get('win_rate', 0.55),
            'profit_factor': decision.get('profit_factor', 1.2),
            'risk_of_ruin': decision.get('risk_of_ruin', 1.0),
            'expected_pnl_per_trade': decision.get('expected_pnl_per_trade', 0),
            'expected_pnl_daily': decision.get('expected_pnl_daily', 0),

            # ===== LEVERAGE =====
            'leverage_recommended': decision.get('leverage_recommended', 1),
            'leverage_max': decision.get('leverage_max', 1),

            # ===== CONSENSO =====
            'consensus_direction': decision.get('consensus_direction', 'NEUTRAL'),
            'consensus_score': decision.get('consensus_score', 0),

            # ===== TIEMPO =====
            'time_since_last_trade': decision.get('time_since_last_trade', 0),
            'next_trade_remaining': next_est.get('remaining_minutes', 0),
            'next_trade_confidence': next_est.get('confidence', 0),

            # ===== BREAK EVEN =====
            'be_trigger': decision.get('be_trigger', 0),

            # ===== MÉTRICAS =====
            'avg_duration_used': decision.get('avg_duration_used', 0),
            'trades_per_day_used': decision.get('trades_per_day_used', 0),

            # ===== GENERACIÓN =====
            'generated_at': datetime.now().isoformat()
        }
