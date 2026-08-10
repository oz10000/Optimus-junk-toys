# signal_generator.py
from typing import Dict, Optional
from datetime import datetime

class SignalGenerator:
    @staticmethod
    def generate(decision: Dict) -> Dict:
        """Siempre devuelve una señal, incluso si es NEUTRAL o HOLD."""
        if decision is None:
            return SignalGenerator._empty_signal()

        action = decision.get('action', 'HOLD')
        direction = decision.get('direction', 'NEUTRAL')
        entry = decision.get('entry_price', 0)

        # Si es HOLD, dirección NEUTRAL
        if action == 'HOLD':
            direction = 'NEUTRAL'

        tp_pct = decision.get('tp_pct', 0.04)
        if direction == 'LONG':
            tp_price = entry * (1 + tp_pct)
        elif direction == 'SHORT':
            tp_price = entry * (1 - tp_pct)
        else:
            tp_price = entry

        edge = decision.get('edge', 0)
        confidence = decision.get('confidence', 0)
        approved = edge > CONFIG.edge_threshold_low and confidence > CONFIG.confidence_threshold

        return {
            'symbol': decision.get('symbol', 'unknown'),
            'direction': direction,
            'action': action,
            'timestamp': decision.get('timestamp', datetime.now()),
            'entry': entry,
            'sl': decision.get('sl_price', 0),
            'tp': tp_price,
            'sl_pct': decision.get('sl_pct', 0.02),
            'tp_pct': tp_pct,
            'edge': edge,
            'edge_pct': edge * 100,
            'confidence': confidence,
            'approved': approved,
            'classification': decision.get('classification', 'Sin señal'),
            'label': decision.get('label', 'N/A'),
            'score': decision.get('score', 0),
            'regime': decision.get('regime', 'Normal'),
            'volatility': decision.get('volatility', 0),
            'win_rate': decision.get('win_rate', 0),
            'profit_factor': decision.get('profit_factor', 0),
            'risk_of_ruin': decision.get('risk_of_ruin', 1.0),
            'expected_pnl_per_trade': decision.get('expected_pnl_per_trade', 0),
            'leverage_recommended': decision.get('leverage_recommended', 1),
            'next_trade_remaining': decision.get('next_trade_est', {}).get('remaining_minutes', 0),
            'next_trade_confidence': decision.get('next_trade_est', {}).get('confidence', 0),
        }

    @staticmethod
    def _empty_signal():
        return {
            'symbol': 'N/A',
            'direction': 'NEUTRAL',
            'action': 'HOLD',
            'timestamp': datetime.now(),
            'entry': 0,
            'sl': 0,
            'tp': 0,
            'sl_pct': 0,
            'tp_pct': 0,
            'edge': 0,
            'edge_pct': 0,
            'confidence': 0,
            'approved': False,
            'classification': 'Sin datos',
            'label': 'N/A',
            'score': 0,
            'regime': 'Normal',
            'volatility': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'risk_of_ruin': 1.0,
            'expected_pnl_per_trade': 0,
            'leverage_recommended': 1,
            'next_trade_remaining': 0,
            'next_trade_confidence': 0,
        }
