# junktoys_level.py
"""
JUNKTOY Level Ω — Mide el coste de oportunidad de no ejecutar una señal.
Basado en evidencia estadística histórica.
"""

import numpy as np
from typing import Dict, List

class JunkToyLevel:
    """Calcula el nivel JUNKTOY (0–10) para una oportunidad."""

    def __init__(self, history: List[Dict], backtest_results: Dict, wf_results: Dict, mc_results: Dict):
        self.history = history
        self.backtest = backtest_results
        self.wf = wf_results
        self.mc = mc_results

    def compute(self, signal: Dict) -> Dict:
        """
        Retorna el nivel JUNKTOY y sus componentes.
        """
        # Factores de ponderación
        weights = {
            'expected_edge': 0.25,
            'win_rate': 0.15,
            'profit_factor': 0.15,
            'expectancy': 0.10,
            'consensus': 0.10,
            'regime': 0.08,
            'volatility': 0.07,
            'liquidity': 0.05,
            'historical_similarity': 0.05,
        }

        scores = {}

        # 1. Expected Edge (normalizado 0-1)
        edge = signal['edge_data']['expected_edge']
        scores['expected_edge'] = min(1.0, edge / 0.70)

        # 2. Win Rate esperado (normalizado 0-1)
        wr = signal['win_rate']
        scores['win_rate'] = min(1.0, wr / 0.85)

        # 3. Profit Factor esperado
        pf = signal['profit_factor']
        scores['profit_factor'] = min(1.0, pf / 2.0)

        # 4. Expectancy (normalizado 0-1)
        exp = signal['edge_data']['expected_pnl_per_trade'] / 100
        scores['expectancy'] = min(1.0, exp / 0.02)

        # 5. Consenso Multi-Timeframe
        consensus = signal['consensus']['confidence']
        scores['consensus'] = consensus

        # 6. Régimen de mercado
        regime_factor = {
            'Expansión': 1.0,
            'Tendencia Fuerte': 0.9,
            'Tendencia': 0.7,
            'Normal': 0.5,
            'Chop': 0.2
        }.get(signal['regime'], 0.5)
        scores['regime'] = regime_factor

        # 7. Volatilidad (normalizada: volatilidad óptima ~1.5%)
        vol = signal['volatility']
        scores['volatility'] = 1 - min(1.0, abs(vol - 1.5) / 5.0)

        # 8. Liquidez (volumen relativo)
        vol_ratio = signal.get('volume_ratio', 1.0)
        scores['liquidity'] = min(1.0, vol_ratio / 2.0)

        # 9. Similitud histórica (porcentaje de veces que señales similares fueron ganadoras)
        scores['historical_similarity'] = self._historical_similarity(signal)

        # Calcular nivel ponderado
        raw_score = sum(scores[k] * weights[k] for k in weights)
        level = raw_score * 10  # escala 0-10

        # Ajuste por robustez fuera de muestra
        wf_win_rate = self.wf.get('avg_win_rate', 0.85)
        mc_ruin = self.mc.get('ruin_prob', 0.005)
        robustness_penalty = 0
        if wf_win_rate < 0.80:
            robustness_penalty += 0.5
        if mc_ruin > 0.02:
            robustness_penalty += 0.5
        level = max(0, min(10, level - robustness_penalty))

        # Interpretación
        if level >= 8.5:
            interpretation = "Confluencia excepcional. Ignorar reduce significativamente la Expectancy y el PF."
        elif level >= 7.0:
            interpretation = "Evidencia histórica fuerte. Omitir deteriora el rendimiento del sistema."
        elif level >= 5.0:
            interpretation = "Ventaja sólida. Ignorar empieza a afectar el rendimiento."
        elif level >= 3.0:
            interpretation = "Ventaja moderada. El impacto de omitirla es limitado."
        else:
            interpretation = "Ventaja débil. Omitir apenas afecta el rendimiento esperado."

        return {
            'level': round(level, 1),
            'raw_score': raw_score,
            'components': scores,
            'interpretation': interpretation,
            'robustness_penalty': robustness_penalty
        }

    def _historical_similarity(self, signal: Dict) -> float:
        """Calcula similitud con patrones históricos ganadores."""
        if not self.history or len(self.history) < 10:
            return 0.5

        # Características relevantes
        features = {
            'score': signal['score'],
            'adx': signal['adx'],
            'ker': signal['ker'],
            'regime': signal['regime'],
            'volatility': signal['volatility']
        }

        # Buscar trades similares en el historial y su resultado
        wins = 0
        total = 0
        for t in self.history:
            if abs(t.get('score', 0) - features['score']) < 0.1 and \
               abs(t.get('adx', 0) - features['adx']) < 5 and \
               t.get('regime') == features['regime']:
                total += 1
                if t.get('pnl_pct', 0) > 0:
                    wins += 1

        if total == 0:
            return 0.5
        return wins / total
