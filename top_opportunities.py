# top_opportunities.py
import numpy as np
from typing import Dict, List

class TopOpportunities:
    @staticmethod
    def compute(signals: List[Dict]) -> Dict:
        longs = [s for s in signals if s.get('direction') == 'LONG']
        shorts = [s for s in signals if s.get('direction') == 'SHORT']
        neutrals = [s for s in signals if s.get('direction') == 'NEUTRAL']

        longs_enriched = [TopOpportunities._enrich_signal(s) for s in longs]
        shorts_enriched = [TopOpportunities._enrich_signal(s) for s in shorts]
        neutrals_enriched = [TopOpportunities._enrich_signal(s) for s in neutrals]

        all_signals = longs_enriched + shorts_enriched + neutrals_enriched
        all_sorted = sorted(all_signals, key=lambda x: x.get('edge', 0), reverse=True)

        # ===== TOP 5 (cambiado de 3 a 5) =====
        if not all_sorted:
            longs = [TopOpportunities._dummy_signal('LONG') for _ in range(5)]
            shorts = [TopOpportunities._dummy_signal('SHORT') for _ in range(5)]
        else:
            longs = [s for s in all_sorted if s.get('direction') == 'LONG'][:5]
            shorts = [s for s in all_sorted if s.get('direction') == 'SHORT'][:5]
            # Rellenar con neutros si faltan
            while len(longs) < 5:
                longs.append(TopOpportunities._dummy_signal('LONG'))
            while len(shorts) < 5:
                shorts.append(TopOpportunities._dummy_signal('SHORT'))

        return {
            'top_long': longs,
            'top_short': shorts,
            'all_signals': all_sorted,
            'timestamp': np.datetime64('now').astype(str),
            'total_signals': len(signals),
            'approved_count': sum(1 for s in signals if s.get('approved', False)),
            'unapproved_count': sum(1 for s in signals if not s.get('approved', False))
        }

    @staticmethod
    def _enrich_signal(signal: Dict) -> Dict:
        edge = signal.get('edge', 0)
        confidence = signal.get('confidence', 0.5)
        approved = signal.get('approved', False)
        score = (edge * 100 * 0.6) + (confidence * 100 * 0.4)
        score = min(100, max(0, score))
        pf = signal.get('profit_factor', 1.0)
        expected_pf = pf * (1 + edge * 0.5)

        signal['approved'] = approved
        signal['score'] = round(score, 2)
        signal['expected_profit_factor'] = round(expected_pf, 2)
        signal['probability'] = min(1.0, 0.3 + edge * 0.7)
        signal['shun_toy_score'] = round(edge * 10, 2)
        return signal

    @staticmethod
    def _dummy_signal(direction='NEUTRAL'):
        return {
            'symbol': '---',
            'direction': direction,
            'entry_price': 0,
            'expected_edge': 0,
            'expected_edge_pct': 0,
            'confidence': 0,
            'score': 0,
            'probability': 0,
            'expected_profit_factor': 1.0,
            'shun_toy_score': 0,
            'temporal_confidence': 0,
            'regime': 'Normal',
            'volatility': 0,
            'approved': False,
            'classification': 'Sin señal',
            'label': 'N/A',
            'edge': 0,
            'win_rate': 0,
            'profit_factor': 1.0,
        }
