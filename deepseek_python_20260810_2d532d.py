# decision_engine.py
from typing import Dict, Optional
from datetime import datetime
from config import CONFIG
from indicators import Indicators
from pidelta import PiDeltaScore
from market_regime import MarketRegime
from consensus import MultiTimeframeConsensus
from expected_edge import ExpectedEdge
from leverage_engine import LeverageEngine
from streak_engine import StreakEngine
from timing_engine import TimingEngine
from risk_manager import RiskManager
from position_manager import PositionManager

class DecisionEngine:
    """Motor de decisión que integra todos los componentes."""

    def __init__(self, data_provider, statistics, history):
        self.data = data_provider
        self.stats = statistics
        self.history = history
        self.consensus = MultiTimeframeConsensus(data_provider)
        self.streak = StreakEngine(history) if history else None
        self.timing = TimingEngine(history) if history else None
        self.risk = RiskManager(self.streak)
        self.position = None

    def evaluate(self, symbol: str, df) -> Optional[Dict]:
        """Evalúa una oportunidad y retorna decisión completa."""
        if df is None or df.empty:
            return None

        # ===== INDICADORES =====
        adx = Indicators.adx(df, 14)
        ker = Indicators.ker(df, 10)
        atr = Indicators.atr(df, 14)
        close = df['close'].iloc[-1]
        volatility = Indicators.volatility(df, 20)
        volume_ratio = Indicators.volume_ratio(df, 20)
        score = PiDeltaScore.compute(df)
        regime = MarketRegime.detect(df)

        # ===== FILTROS =====
        if abs(score) < CONFIG.min_score:
            return None
        if adx < CONFIG.adx_threshold:
            return None
        if ker < CONFIG.ker_threshold:
            return None
        if regime == 'Chop':
            return None

        # ===== CONSENSO MULTI-TIMEFRAME =====
        consensus = self.consensus.compute(symbol)
        if consensus['direction'] == 'NEUTRAL':
            return None

        # ===== DIRECCIÓN =====
        direction = 'LONG' if score > 0 else 'SHORT'
        if consensus['direction'] != 'NEUTRAL' and consensus['direction'] != direction:
            # Desacuerdo entre consenso y señal local
            if consensus['confidence'] > 0.5:
                direction = consensus['direction']

        # ===== SL / TP =====
        entry_price = close
        sl_price = entry_price * (1 - CONFIG.sl_mult * atr / entry_price) if direction == 'LONG' else entry_price * (1 + CONFIG.sl_mult * atr / entry_price)
        tp_price = entry_price * (1 + CONFIG.tp_mult * atr / entry_price) if direction == 'LONG' else entry_price * (1 - CONFIG.tp_mult * atr / entry_price)

        # ===== MÉTRICAS HISTÓRICAS =====
        metrics = self.stats.get_metrics(symbol) if self.stats else {}
        win_rate = metrics.get('win_rate', 0.55)
        pf = metrics.get('profit_factor', 1.2)

        # ===== EXPECTED EDGE =====
        tp_pct = abs((tp_price / entry_price - 1) * 100)
        sl_pct = abs((sl_price / entry_price - 1) * 100)
        edge_data = ExpectedEdge.compute(
            score, adx, ker, atr/entry_price*100, regime,
            win_rate, pf, tp_pct, sl_pct
        )

        if edge_data['expected_edge'] < 0.10:
            return None

        # ===== APALANCAMIENTO =====
        lev = LeverageEngine.compute(
            atr/entry_price*100, win_rate, pf,
            metrics.get('max_drawdown', 0.08),
            edge_data['confidence']
        )

        # ===== POSITION SIZE =====
        size = self.risk.get_position_size(
            CONFIG.initial_capital,
            lev['recommended'],
            entry_price
        )

        # ===== ESTIMACIÓN DE TIEMPO =====
        next_est = self.timing.estimate_next_trade(symbol) if self.timing else {'remaining_minutes': 45, 'confidence': 0.5}

        # ===== DECISIÓN =====
        return {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'score': score,
            'adx': adx,
            'ker': ker,
            'atr': atr,
            'regime': regime,
            'volatility': volatility,
            'volume_ratio': volume_ratio,
            'consensus': consensus,
            'edge_data': edge_data,
            'leverage': lev,
            'position_size': size,
            'next_trade_est': next_est,
            'timestamp': df.index[-1],
            'classification': edge_data['classification'],
            'label': edge_data['label'],
            'confidence': edge_data['confidence'],
            'win_rate': win_rate,
            'profit_factor': pf,
            'risk_of_ruin': edge_data['risk_of_ruin'],
            'expected_pnl_hour': edge_data['expected_pnl_per_hour'],
            'expected_pnl_day': edge_data['expected_pnl_daily'],
            'be_trigger': edge_data['be_trigger'] if 'be_trigger' in edge_data else 0.004,
        }

    def manage_position(self, current_price: float) -> Dict:
        """Actualiza la posición activa."""
        if self.position is None:
            return {'status': 'no_position'}

        events = self.position.update(current_price)
        if events.get('events'):
            return {'status': 'closed', 'events': events['events'], 'pnl': events['pnl_pct']}
        return {'status': 'open', 'events': [], 'pnl': events['pnl_pct']}