# decision_engine.py
import numpy as np
import pandas as pd
from typing import Dict, Optional
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
    """
    Motor de decisión principal.
    Integra indicadores, consenso, expected edge, régimen y apalancamiento.
    """

    def __init__(self, data_provider, statistics, history):
        self.data = data_provider
        self.stats = statistics or {}
        self.history = history or []
        self.regime_detector = MarketRegime()
        self.timing = TimingEngine(self.history) if len(self.history) >= 2 else None

    def evaluate(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Evalúa una vela y retorna una decisión de trading completa.
        """
        if df is None or len(df) < 100:
            return self._empty_decision(symbol)

        # 1. Calcular indicadores
        indicators = Indicators.compute(df)
        if indicators is None:
            return self._empty_decision(symbol)

        last_price = df['close'].iloc[-1]

        # 2. Detectar régimen de mercado
        regime = self.regime_detector.detect(df)

        # 3. Calcular volatilidad
        volatility = df['close'].pct_change().std() * np.sqrt(252)

        # 4. Extraer valores de indicadores
        pidelta = indicators.get('pidelta', 0.0)
        adx = indicators.get('adx', 25.0)
        ker = indicators.get('ker', 0.3)
        atr = indicators.get('atr', 0.0)
        atr_pct = atr / last_price if last_price > 0 else 0.01

        # 5. Consenso multi-timeframe
        consensus_score = Consensus.compute(df)

        # 6. Expected Edge
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

        # 7. Decisión final
        if edge > 0.30 and pidelta > 0.15:
            action = 'BUY'
            direction = 'LONG'
        elif edge > 0.30 and pidelta < -0.15:
            action = 'SELL'
            direction = 'SHORT'
        else:
            action = 'HOLD'
            direction = 'NEUTRAL'

        # 8. Calcular precios de SL y TP
        sl_pct = CONFIG.sl_pct
        tp_pct = CONFIG.tp_pct
        sl_price = last_price * (1 - sl_pct) if direction == 'LONG' else last_price * (1 + sl_pct)
        tp_price = last_price * (1 + tp_pct) if direction == 'LONG' else last_price * (1 - tp_pct)

        # 9. Calcular apalancamiento
        leverage = LeverageEngine.compute(edge, edge_data.get('confidence', 0.5))

        # 10. Obtener estimación temporal
        time_since_last = 0
        next_trade_est = {'remaining_minutes': 0, 'confidence': 0}
        if self.timing is not None:
            est = self.timing.estimate_next_trade()
            time_since_last = est.get('elapsed', 0)
            next_trade_est = {
                'remaining_minutes': est.get('remaining_minutes', 0),
                'confidence': est.get('confidence', 0)
            }

        # 11. Break Even trigger
        be_trigger = CONFIG.be_trigger

        # 12. Retornar decisión completa
        return {
            # ===== ACCIÓN =====
            'action': action,
            'direction': direction,
            'symbol': symbol,
            'timestamp': datetime.now(),

            # ===== PRECIOS =====
            'entry_price': last_price,
            'sl_price': sl_price,
            'tp_price': sl_price,  # Se recalcula en signal_generator
            'sl_pct': sl_pct,
            'tp_pct': tp_pct,

            # ===== SCORING =====
            'score': pidelta,
            'adx': adx,
            'ker': ker,
            'regime': regime,
            'volatility': volatility,
            'atr': atr,
            'pidelta': pidelta,
            'consensus_score': consensus_score,

            # ===== EXPECTED EDGE =====
            'edge_data': edge_data,
            'edge': edge,
            'edge_pct': edge * 100,
            'classification': edge_data.get('classification', 'Evitar'),
            'label': edge_data.get('label', 'E'),
            'confidence': edge_data.get('confidence', 0.5),
            'win_rate': edge_data.get('win_rate', 0.55),
            'profit_factor': edge_data.get('profit_factor', 1.2),
            'risk_of_ruin': edge_data.get('risk_of_ruin', 1.0),
            'expected_pnl_per_trade': edge_data.get('expected_pnl_per_trade', 0),
            'expected_pnl_daily': edge_data.get('expected_pnl_daily', 0),

            # ===== LEVERAGE =====
            'leverage_recommended': leverage,
            'leverage_max': CONFIG.max_leverage,

            # ===== CONSENSO =====
            'consensus_direction': 'BULL' if consensus_score > 0.2 else 'BEAR' if consensus_score < -0.2 else 'NEUTRAL',
            'consensus_score': consensus_score,

            # ===== TIEMPO =====
            'time_since_last_trade': time_since_last,
            'next_trade_est': next_trade_est,

            # ===== BREAK EVEN =====
            'be_trigger': be_trigger,

            # ===== MÉTRICAS ADICIONALES =====
            'avg_duration_used': edge_data.get('avg_duration_used', 1.5),
            'trades_per_day_used': edge_data.get('trades_per_day_used', 1.2),
        }

    def _empty_decision(self, symbol: str) -> Dict:
        """Retorna una decisión vacía cuando no hay datos suficientes."""
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
