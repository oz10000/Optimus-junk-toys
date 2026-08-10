# signal_generator.py
from typing import Dict
import pandas as pd
from datetime import datetime

class SignalGenerator:
    """Genera señales formateadas a partir de decisiones."""

    @staticmethod
    def generate(decision: Dict) -> Dict:
        """Convierte una decisión en señal completa."""
        if decision is None:
            return None

        return {
            # ===== IDENTIFICACIÓN =====
            'symbol': decision['symbol'],
            'direction': decision['direction'],
            'timestamp': decision['timestamp'],

            # ===== PRECIOS =====
            'entry': decision['entry_price'],
            'sl': decision['sl_price'],
            'tp': decision['tp_price'],

            # ===== SCORING =====
            'score': decision['score'],
            'adx': decision['adx'],
            'ker': decision['ker'],
            'regime': decision['regime'],
            'volatility': decision['volatility'],

            # ===== EXPECTED EDGE =====
            'edge': decision['edge_data']['expected_edge'],
            'edge_pct': decision['edge_data']['expected_edge_pct'],
            'classification': decision['classification'],
            'label': decision['label'],
            'confidence': decision['confidence'],
            'win_rate': decision['win_rate'],
            'profit_factor': decision['profit_factor'],
            'risk_of_ruin': decision['risk_of_ruin'],

            # ===== PNL =====
            'expected_pnl_hour': decision['expected_pnl_hour'],
            'expected_pnl_day': decision['expected_pnl_day'],

            # ===== LEVERAGE & SIZE =====
            'leverage_recommended': decision['leverage']['recommended'],
            'leverage_max': decision['leverage']['max_safe'],
            'position_size': decision['position_size'],

            # ===== CONSENSO =====
            'consensus': decision['consensus']['direction'],
            'consensus_score': decision['consensus']['score'],
            'consensus_contributions': decision['consensus']['contributions'],

            # ===== TIEMPO =====
            'time_since_last_trade': decision.get('time_since_last_trade', 0),
            'next_trade_estimate': decision['next_trade_est']['remaining_minutes'],
            'next_trade_confidence': decision['next_trade_est']['confidence'],

            # ===== BREAK EVEN =====
            'be_trigger': decision['be_trigger'],

            # ===== TIMESTAMP =====
            'generated_at': datetime.now().isoformat()
        }
