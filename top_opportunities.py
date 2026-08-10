# top_opportunities.py
import numpy as np
from typing import Dict, List


class TopOpportunities:
    """
    Genera el TOP 3 LONG y TOP 3 SHORT.
    Incluye señales aprobadas y desaprobadas.
    """

    # Umbral para considerar una señal "aprobada"
    APPROVAL_EDGE_THRESHOLD = 0.10
    APPROVAL_CONFIDENCE_THRESHOLD = 0.40

    @staticmethod
    def compute(signals: List[Dict]) -> Dict:
        """
        Calcula el TOP 3 LONG y TOP 3 SHORT.
        Cada señal incluye un campo 'approved' indicando si supera los umbrales.
        """
        # Separar por dirección
        longs = [s for s in signals if s.get('direction') == 'LONG']
        shorts = [s for s in signals if s.get('direction') == 'SHORT']

        # Enriquecer cada señal con el estado de aprobación
        longs_enriched = [TopOpportunities._enrich_signal(s) for s in longs]
        shorts_enriched = [TopOpportunities._enrich_signal(s) for s in shorts]

        # Ordenar por edge (independientemente de aprobación)
        longs_sorted = sorted(longs_enriched, key=lambda x: x.get('edge', 0), reverse=True)
        shorts_sorted = sorted(shorts_enriched, key=lambda x: x.get('edge', 0), reverse=True)

        return {
            'top_long': TopOpportunities._format_top(longs_sorted[:3], 'LONG'),
            'top_short': TopOpportunities._format_top(shorts_sorted[:3], 'SHORT'),
            'all_long': TopOpportunities._format_all(longs_sorted, 'LONG'),
            'all_short': TopOpportunities._format_all(shorts_sorted, 'SHORT'),
            'timestamp': np.datetime64('now').astype(str),
            'total_signals': len(signals),
            'approved_count': sum(1 for s in signals if TopOpportunities._is_approved(s)),
            'unapproved_count': sum(1 for s in signals if not TopOpportunities._is_approved(s))
        }

    @staticmethod
    def _is_approved(signal: Dict) -> bool:
        """Determina si una señal es considerada 'aprobada'."""
        edge = signal.get('edge', 0)
        confidence = signal.get('confidence', 0)
        return edge > TopOpportunities.APPROVAL_EDGE_THRESHOLD and confidence > TopOpportunities.APPROVAL_CONFIDENCE_THRESHOLD

    @staticmethod
    def _enrich_signal(signal: Dict) -> Dict:
        """Añade el campo 'approved' y calcula score."""
        edge = signal.get('edge', 0)
        confidence = signal.get('confidence', 0.5)
        approved = TopOpportunities._is_approved(signal)

        # Score combinado (0-100)
        score = (edge * 100 * 0.6) + (confidence * 100 * 0.4)
        score = min(100, max(0, score))

        # Profit Factor esperado
        pf = signal.get('profit_factor', 1.0)
        expected_pf = pf * (1 + edge * 0.5)

        # Probabilidad
        probability = min(1.0, 0.3 + edge * 0.7)

        signal['approved'] = approved
        signal['score'] = round(score, 2)
        signal['expected_profit_factor'] = round(expected_pf, 2)
        signal['probability'] = round(probability, 3)
        signal['shun_toy_score'] = round(edge * 10, 2)

        return signal

    @staticmethod
    def _format_top(top: List[Dict], direction: str) -> List[Dict]:
        """Formatea el TOP 3 para mostrar."""
        result = []
        for signal in top:
            result.append({
                'symbol': signal.get('symbol', 'unknown'),
                'direction': direction,
                'entry_price': signal.get('entry', 0),
                'expected_edge': signal.get('edge', 0),
                'expected_edge_pct': signal.get('edge', 0) * 100,
                'confidence': signal.get('confidence', 0.5),
                'score': signal.get('score', 0),
                'probability': signal.get('probability', 0),
                'expected_profit_factor': signal.get('expected_profit_factor', 1.0),
                'shun_toy_score': signal.get('shun_toy_score', 0),
                'temporal_confidence': signal.get('next_trade_confidence', 0.5),
                'regime': signal.get('regime', 'Normal'),
                'volatility': signal.get('volatility', 0),
                'approved': signal.get('approved', False),
                'classification': signal.get('classification', 'Evitar'),
                'label': signal.get('label', 'E'),
                'edge': signal.get('edge', 0),
                'win_rate': signal.get('win_rate', 0),
                'profit_factor': signal.get('profit_factor', 1.0),
            })
        return result

    @staticmethod
    def _format_all(signals: List[Dict], direction: str) -> List[Dict]:
        """Formatea todas las señales para el ranking completo."""
        result = []
        for signal in signals:
            result.append({
                'symbol': signal.get('symbol', 'unknown'),
                'direction': direction,
                'edge': signal.get('edge', 0),
                'edge_pct': signal.get('edge', 0) * 100,
                'confidence': signal.get('confidence', 0.5),
                'score': signal.get('score', 0),
                'approved': signal.get('approved', False),
                'classification': signal.get('classification', 'Evitar'),
                'label': signal.get('label', 'E'),
            })
        return result
