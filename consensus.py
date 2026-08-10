# consensus.py
from typing import Dict
import numpy as np
from config import CONFIG
from pidelta import PiDeltaScore

class MultiTimeframeConsensus:
    """Consenso ponderado de múltiples timeframes."""

    def __init__(self, data_provider):
        self.data = data_provider

    def compute(self, symbol: str) -> Dict:
        weights = CONFIG.mtf_weights
        contributions = {}
        weighted_sum = 0.0
        total_weight = 0.0

        for tf, weight in weights.items():
            if weight == 0:
                continue
            df = self.data.get_ohlcv(symbol, timeframe=tf, limit=100)
            if df is None or df.empty:
                continue
            score = PiDeltaScore.compute(df)
            signal = 1 if score > CONFIG.min_score else -1 if score < -CONFIG.min_score else 0
            contributions[tf] = {'score': score, 'signal': signal, 'weight': weight}
            weighted_sum += weight * signal
            total_weight += weight

        if total_weight == 0:
            return {'direction': 'NEUTRAL', 'confidence': 0.0, 'score': 0.0, 'contributions': {}}

        consensus_score = weighted_sum / total_weight
        direction = 'LONG' if consensus_score > 0.3 else 'SHORT' if consensus_score < -0.3 else 'NEUTRAL'

        return {
            'direction': direction,
            'confidence': abs(consensus_score),
            'score': consensus_score,
            'contributions': contributions
        }
