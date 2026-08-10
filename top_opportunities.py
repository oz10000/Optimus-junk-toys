# top_opportunities.py
import numpy as np
from typing import Dict, List, Optional

class TopOpportunities:
    """
    Genera el TOP 3 LONG y TOP 3 SHORT con scoring completo.
    """
    
    @staticmethod
    def compute(signals: List[Dict]) -> Dict:
        """
        Calcula el TOP 3 LONG y TOP 3 SHORT.
        
        Args:
            signals: Lista de señales con todos los datos de edge
        
        Returns:
            Dict con top_long, top_short, y métricas agregadas
        """
        longs = [s for s in signals if s.get('direction') == 'LONG']
        shorts = [s for s in signals if s.get('direction') == 'SHORT']
        
        # Ordenar por Expected Edge
        longs_sorted = sorted(longs, key=lambda x: x.get('edge', 0), reverse=True)
        shorts_sorted = sorted(shorts, key=lambda x: x.get('edge', 0), reverse=True)
        
        top_long = TopOpportunities._enrich(top=longs_sorted[:3], direction='LONG')
        top_short = TopOpportunities._enrich(top=shorts_sorted[:3], direction='SHORT')
        
        return {
            'top_long': top_long,
            'top_short': top_short,
            'timestamp': np.datetime64('now').astype(str)
        }
    
    @staticmethod
    def _enrich(top: List[Dict], direction: str) -> List[Dict]:
        """Enriquece cada señal con métricas adicionales."""
        enriched = []
        for signal in top:
            edge_data = signal.get('edge_data', {})
            
            # Calcular Score (0-100) combinando edge y confianza
            edge = signal.get('edge', 0)
            confidence = signal.get('confidence', 0.5)
            score = (edge * 100 * 0.6) + (confidence * 100 * 0.4)
            score = min(100, max(0, score))
            
            # Profit Factor esperado
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
                'shun_toy_score': edge * 10,  # Simplificado, se integrará con ShunToyLevel
                'temporal_confidence': signal.get('next_trade_confidence', 0.5),
                'regime': signal.get('regime', 'Normal'),
                'volatility': signal.get('volatility', 0)
            })
        
        return enriched
