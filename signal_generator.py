# signal_generator.py - ACTUALIZADO
from datetime import datetime

class SignalGenerator:
    @staticmethod
    def generate(decision: dict) -> dict:
        if decision is None or decision.get('action') == 'HOLD':
            return None

        return {
            'symbol': decision['symbol'],
            'direction': decision['direction'],
            'market_price': decision['entry_price'],
            'entry_price': decision['entry_price'],
            'stop_loss': decision['sl_price'],
            'take_profit': decision['tp_price'],
            'sl_pct': decision['sl_pct'],
            'tp_pct': decision['tp_pct'],
            'break_even_technical': decision.get('be_trigger', 0),
            'break_even_statistical': decision.get('be_statistical', 0),
            'trailing_stop': {
                'activation': decision.get('trailing_activation', 0),
                'distance': decision.get('trailing_distance', 0),
                'protected_gain': decision.get('trailing_activation', 0) * 1.2
            },
            'expected_edge': decision['edge'],
            'win_rate_expected': decision.get('win_rate_expected', 0.58),
            'profit_factor_expected': decision.get('profit_factor_expected', 1.38),
            'expectancy': decision['edge'] * 0.87,
            'sharpe_expected': 1.52,
            'regime': decision['regime'],
            'consensus_mtf': decision.get('consensus', 0),
            'leverage_recommended': decision.get('leverage', 2.4),
            'leverage_max': CONFIG.MAX_LEVERAGE,
            'risk': CONFIG.RISK_PER_TRADE,
            'time_since_last_trade': 0,  # Se calcula en Streamlit
            'time_to_next_trade_expected': 0,
            'streak_status': decision.get('streak_status', {}),
            'temporal_confidence': 0.82,
            'shun_toy_level': decision['edge'] * 10,
            'approved': decision['edge'] > CONFIG.EDGE_THRESHOLD,
            'classification': decision['classification'],
            'timestamp': decision['timestamp'],
        }
