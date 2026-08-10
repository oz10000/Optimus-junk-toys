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

    def evaluate(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Evalúa una vela y retorna una decisión de trading.
        """
        if df is None or len(df) < 100:
            return {'action': 'HOLD'}

        # 1. Calcular indicadores
        indicators = Indicators.compute(df)
        if indicators is None:
            return {'action': 'HOLD'}

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
        elif edge > 0.30 and pidelta < -0.15:
            action = 'SELL'
        else:
            action = 'HOLD'

        # 8. Retornar decisión completa
        return {
            'action': action,
            'symbol': symbol,
            'entry': last_price,
            'sl_pct': CONFIG.sl_pct,
            'tp_pct': CONFIG.tp_pct,
            'edge_data': edge_data,
            'regime': regime,
            'volatility': volatility,
            'atr': atr,
            'adx': adx,
            'pidelta': pidelta,
            'consensus_score': consensus_score,
            'timestamp': datetime.now()
        }
