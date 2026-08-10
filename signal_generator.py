# signal_generator.py - VERSIÓN CON CAMPOS COMPLETOS
from datetime import datetime
from config import CONFIG


class SignalGenerator:
    @staticmethod
    def generate(decision: dict) -> dict:
        if decision is None or decision.get('action') == 'HOLD':
            return None

        symbol = decision.get('symbol', 'BTC/USDT')
        thresholds = CONFIG.get_thresholds(symbol)

        return {
            'symbol': symbol,
            'direction': decision.get('direction', 'NEUTRAL'),
            'market_price': decision.get('entry_price', 0),
            'entry_price': decision.get('entry_price', 0),
            'entry_range': {
                'low': decision.get('entry_price', 0) * 0.998,
                'high': decision.get('entry_price', 0) * 1.002
            },
            'stop_loss': decision.get('sl_price', 0),
            'take_profit': decision.get('tp_price', 0),
            'sl_pct': decision.get('sl_pct', 0.016),
            'tp_pct': decision.get('tp_pct', 0.038),
            'break_even_technical': decision.get('be_trigger', 0.0035),
            'break_even_statistical': decision.get('be_statistical', 0.0025),
            'be_activation_price': decision.get('entry_price', 0) * (1 + decision.get('be_trigger', 0.0035)),
            'min_protected_gain': decision.get('be_trigger', 0.0035) * 0.5,
            'trailing_stop': {
                'activation': decision.get('trailing_activation', 0.012),
                'distance': decision.get('trailing_distance', 0.006),
                'protected_gain': decision.get('trailing_activation', 0.012) * 1.2
            },
            'expected_edge': decision.get('edge', 0),
            'edge_pct': decision.get('edge', 0) * 100,
            'win_rate_expected': decision.get('win_rate_expected', 0.94 if CONFIG.FIRM_MODE else 0.86),
            'profit_factor_expected': decision.get('profit_factor_expected', 2.45 if CONFIG.FIRM_MODE else 1.58),
            'expectancy': decision.get('edge', 0) * 0.87,
            'sharpe_expected': 2.10 if CONFIG.FIRM_MODE else 1.52,
            'regime': decision.get('regime', 'Normal'),
            'consensus_mtf': decision.get('consensus_score', 0),
            'consensus_direction': decision.get('consensus_direction', 'NEUTRAL'),
            'leverage_recommended': decision.get('leverage_recommended', 6),
            'leverage_max': decision.get('leverage_max', 8),
            'risk': CONFIG.RISK_PER_TRADE,
            'time_since_last_trade': decision.get('time_since_last_trade', 0),
            'time_to_next_trade_expected': decision.get('next_trade_est', {}).get('remaining_minutes', 0),
            'time_to_tp_expected': decision.get('avg_duration_used', 1.5) * 0.5,
            'streak_status': decision.get('streak_status', {}),
            'temporal_confidence': decision.get('next_trade_est', {}).get('confidence', 0),
            'shun_toy_level': decision.get('edge', 0) * 10,
            'approved': decision.get('edge', 0) > CONFIG.get_thresholds(symbol)['edge'],
            'classification': decision.get('classification', 'Sin datos'),
            'confidence': decision.get('confidence', 0),
            'timestamp': decision.get('timestamp', datetime.now()),
        }
