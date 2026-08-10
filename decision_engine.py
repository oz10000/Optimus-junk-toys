# decision_engine.py
import numpy as np
import pandas as pd
from typing import Dict
from datetime import datetime

from indicators import Indicators
from consensus import Consensus
from expected_edge import ExpectedEdge
from leverage_engine import LeverageEngine
from risk_manager import RiskManager
from market_regime import MarketRegime
from config import CONFIG
from timing_engine import TimingEngine


class DecisionEngine:
    def __init__(self, data_provider, statistics, history):
        self.data = data_provider
        self.stats = statistics or {}
        self.history = history or []
        self.regime_detector = MarketRegime()
        self.timing = TimingEngine(self.history) if len(self.history) >= 2 else None

    def evaluate(self, symbol: str, df: pd.DataFrame) -> Dict:
        """Siempre retorna una decisión, incluso si es HOLD."""
        if df is None or len(df) < 50:
            return self._empty_decision(symbol)

        try:
            indicators = Indicators.compute(df)
            if indicators is None:
                return self._empty_decision(symbol)

            last_price = df['close'].iloc[-1]
            regime = self.regime_detector.detect(df)
            volatility = df['close'].pct_change().std() * np.sqrt(252)

            pidelta = indicators.get('pidelta', 0.0)
            adx = indicators.get('adx', 25.0)
            ker = indicators.get('ker', 0.3)
            atr = indicators.get('atr', 0.0)
            atr_pct = atr / last_price if last_price > 0 else 0.01

            consensus_score = Consensus.compute(df)

            win_rate = self.stats.get('win_rate', 0.55)
            pf = self.stats.get('profit_factor', 1.2)

            edge_data = ExpectedEdge.compute(
                score=pidelta,
                adx=adx,
                ker=ker,
                atr_pct=atr_pct,
                regime=regime,
                win_rate=win_rate,
                pf=pf,
                tp_pct=CONFIG.tp_pct,
                sl_pct=CONFIG.sl_pct
            )

            edge = edge_data.get('expected_edge', 0.0)

            # Decisión menos restrictiva (genera señales con más frecuencia)
            if pidelta > 0.05 and edge > 0.05:
                action = 'BUY'
                direction = 'LONG'
            elif pidelta < -0.05 and edge > 0.05:
                action = 'SELL'
                direction = 'SHORT'
            else:
                action = 'HOLD'
                direction = 'NEUTRAL'

            sl_price = last_price * (1 - CONFIG.sl_pct) if direction == 'LONG' else last_price * (1 + CONFIG.sl_pct)
            tp_price = last_price * (1 + CONFIG.tp_pct) if direction == 'LONG' else last_price * (1 - CONFIG.tp_pct)
            leverage = LeverageEngine.compute(edge, edge_data.get('confidence', 0.5))

            time_since_last = 0
            next_trade_est = {'remaining_minutes': 0, 'confidence': 0}
            if self.timing is not None:
                est = self.timing.estimate_next_trade()
                time_since_last = est.get('elapsed', 0)
                next_trade_est = {
                    'remaining_minutes': est.get('remaining_minutes', 0),
                    'confidence': est.get('confidence', 0)
                }

            return {
                'action': action,
                'direction': direction,
                'symbol': symbol,
                'timestamp': datetime.now(),
                'entry_price': last_price,
                'sl_price': sl_price,
                'tp_price': tp_price,
                'sl_pct': CONFIG.sl_pct,
                'tp_pct': CONFIG.tp_pct,
                'score': pidelta,
                'adx': adx,
                'ker': ker,
                'regime': regime,
                'volatility': volatility,
                'atr': atr,
                'pidelta': pidelta,
                'consensus_score': consensus_score,
                'edge_data': edge_data,
                'edge': edge,
                'edge_pct': edge * 100,
                'classification': edge_data.get('classification', 'Sin señal'),
                'label': edge_data.get('label', 'N/A'),
                'confidence': edge_data.get('confidence', 0.5),
                'win_rate': edge_data.get('win_rate', 0.55),
                'profit_factor': edge_data.get('profit_factor', 1.2),
                'risk_of_ruin': edge_data.get('risk_of_ruin', 1.0),
                'expected_pnl_per_trade': edge_data.get('expected_pnl_per_trade', 0),
                'expected_pnl_daily': edge_data.get('expected_pnl_daily', 0),
                'leverage_recommended': leverage,
                'leverage_max': CONFIG.max_leverage,
                'consensus_direction': 'BULL' if consensus_score > 0.2 else 'BEAR' if consensus_score < -0.2 else 'NEUTRAL',
                'time_since_last_trade': time_since_last,
                'next_trade_est': next_trade_est,
                'be_trigger': CONFIG.be_trigger,
                'avg_duration_used': edge_data.get('avg_duration_used', 1.5),
                'trades_per_day_used': edge_data.get('trades_per_day_used', 1.2)
            }
        except Exception as e:
            print(f"❌ Error en evaluate para {symbol}: {e}")
            return self._empty_decision(symbol)

    def _empty_decision(self, symbol: str) -> Dict:
        return {
            'action': 'HOLD',
            'direction': 'NEUTRAL',
            'symbol': symbol,
            'timestamp': datetime.now(),
            'entry_price': 0,
            'sl_price': 0,
            'tp_price': 0,
            'sl_pct': 0,
            'tp_pct': 0,
            'score': 0,
            'adx': 0,
            'ker': 0,
            'regime': 'Normal',
            'volatility': 0,
            'atr': 0,
            'pidelta': 0,
            'consensus_score': 0,
            'edge_data': {},
            'edge': 0,
            'edge_pct': 0,
            'classification': 'Sin datos',
            'label': 'N/A',
            'confidence': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'risk_of_ruin': 1.0,
            'expected_pnl_per_trade': 0,
            'expected_pnl_daily': 0,
            'leverage_recommended': 1,
            'leverage_max': 1,
            'consensus_direction': 'NEUTRAL',
            'time_since_last_trade': 0,
            'next_trade_est': {'remaining_minutes': 0, 'confidence': 0},
            'be_trigger': 0,
            'avg_duration_used': 0,
            'trades_per_day_used': 0
        }
