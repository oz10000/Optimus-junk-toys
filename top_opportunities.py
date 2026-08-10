# top_opportunities.py
import numpy as np
from typing import Dict, List

class TopOpportunities:
    @staticmethod
    def compute(signals: List[Dict]) -> Dict:
        longs = [s for s in signals if s.get('direction') == 'LONG']
        shorts = [s for s in signals if s.get('direction') == 'SHORT']
        longs_sorted = sorted(longs, key=lambda x: x.get('edge', 0), reverse=True)
        shorts_sorted = sorted(shorts, key=lambda x: x.get('edge', 0), reverse=True)
        return {
            'top_long': TopOpportunities._enrich(longs_sorted[:3], 'LONG'),
            'top_short': TopOpportunities._enrich(shorts_sorted[:3], 'SHORT'),
            'timestamp': np.datetime64('now').astype(str)
        }

    @staticmethod
    def _enrich(top: List[Dict], direction: str) -> List[Dict]:
        enriched = []
        for signal in top:
            edge = signal.get('edge', 0)
            confidence = signal.get('confidence', 0.5)
            score = (edge * 100 * 0.6) + (confidence * 100 * 0.4)
            score = min(100, max(0, score))
            pf = signal.get('profit_factor', 1.0)
            expected_pf = pf * (1 + edge * 0.5)
            enriched.append({
                'symbol': signal.get('symbol', 'unknown'),
                'direction': direction,
                'entry_price': signal.get('entry', 0),
                'expected_edge': edge,
                'expected_edge_pct': edge * 100,
                'confidence': confidence,
                'score': round(score, 2),
                'probability': min(1.0, 0.3 + edge * 0.7),
                'expected_profit_factor': round(expected_pf, 2),
                'shun_toy_score': edge * 10,
                'temporal_confidence': signal.get('next_trade_confidence', 0.5),
                'regime': signal.get('regime', 'Normal'),
                'volatility': signal.get('volatility', 0)
            })
        return enriched
