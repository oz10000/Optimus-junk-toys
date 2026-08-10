# shun_toy_level.py
import numpy as np
from typing import Dict

class ShunToyLevel:
    """
    Índice ShunToy Level (0-10).
    Mide el coste esperado de ignorar una oportunidad.
    """
    
    @staticmethod
    def compute(edge_data: Dict, market_data: Dict, historical_data: Dict) -> Dict:
        """
        Calcula el ShunToy Level para una oportunidad.
        
        Args:
            edge_data: Datos de Expected Edge
            market_data: Datos de mercado (volatilidad, régimen, etc.)
            historical_data: Datos históricos (win_rate, pf, etc.)
        
        Returns:
            Dict con score (0-10), components y justificación
        """
        # 1. Expected Edge (0-1) → peso 25%
        edge_score = min(edge_data.get('expected_edge', 0) / 0.5, 1.0)
        
        # 2. Profit Factor (0-1) → peso 20%
        pf = historical_data.get('profit_factor', 1.0)
        pf_score = min((pf - 1.0) / 1.0, 1.0)  # PF=1 → 0, PF=2 → 1
        
        # 3. Expectancy (0-1) → peso 15%
        expectancy = historical_data.get('expectancy', 0)
        exp_score = min(abs(expectancy) / 0.02, 1.0)  # 2% → 1
        
        # 4. Walk-Forward consistency (0-1) → peso 10%
        wf_score = historical_data.get('walk_forward_consistency', 0.5)
        
        # 5. Monte Carlo stability (0-1) → peso 10%
        mc_score = historical_data.get('monte_carlo_stability', 0.5)
        
        # 6. Risk of Ruin (0-1, invertido) → peso 10%
        ruin = historical_data.get('risk_of_ruin', 1.0)
        ruin_score = 1 - min(ruin, 1.0)
        
        # 7. Consensus multi-timeframe (0-1) → peso 5%
        consensus_score = edge_data.get('confidence', 0.5)
        
        # 8. Régimen (0-1) → peso 5%
        regime = market_data.get('regime', 'Normal')
        regime_scores = {
            'Expansión': 1.0,
            'Tendencia Fuerte': 0.9,
            'Tendencia': 0.7,
            'Normal': 0.5,
            'Chop': 0.2
        }
        regime_score = regime_scores.get(regime, 0.5)
        
        # Pesos
        weights = {
            'expected_edge': 0.25,
            'profit_factor': 0.20,
            'expectancy': 0.15,
            'walk_forward': 0.10,
            'monte_carlo': 0.10,
            'risk_of_ruin': 0.10,
            'consensus': 0.05,
            'regime': 0.05
        }
        
        # Cálculo del score ponderado
        raw_score = (
            weights['expected_edge'] * edge_score +
            weights['profit_factor'] * pf_score +
            weights['expectancy'] * exp_score +
            weights['walk_forward'] * wf_score +
            weights['monte_carlo'] * mc_score +
            weights['risk_of_ruin'] * ruin_score +
            weights['consensus'] * consensus_score +
            weights['regime'] * regime_score
        )
        
        # Escalar a 0-10
        final_score = raw_score * 10
        
        # Determinar nivel
        if final_score >= 8.0:
            level = 'Ω (Oportunidad excepcional)'
        elif final_score >= 6.0:
            level = 'A (Alta prioridad)'
        elif final_score >= 4.0:
            level = 'M (Media prioridad)'
        elif final_score >= 2.0:
            level = 'B (Baja prioridad)'
        else:
            level = 'E (Evitar)'
        
        return {
            'score': round(final_score, 2),
            'level': level,
            'components': {
                'expected_edge': round(edge_score, 3),
                'profit_factor': round(pf_score, 3),
                'expectancy': round(exp_score, 3),
                'walk_forward': round(wf_score, 3),
                'monte_carlo': round(mc_score, 3),
                'risk_of_ruin': round(ruin_score, 3),
                'consensus': round(consensus_score, 3),
                'regime': round(regime_score, 3)
            },
            'interpretation': f"Coste esperado de ignorar: {final_score:.1f}/10"
        }
