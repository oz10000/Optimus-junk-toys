# timing_engine.py
from datetime import datetime
from typing import Dict, Optional
from distribution_analyzer import DistributionAnalyzer

class TimingEngine:
    def __init__(self, history):
        self.history = history
        self.analyzer = DistributionAnalyzer(history) if len(history) >= 2 else None

    def get_last_trade_time(self) -> Optional[datetime]:
        if not self.history:
            return None
        return self.history[-1].get('timestamp')

    def estimate_next_trade(self) -> Dict:
        """
        Estima el tiempo hasta el próximo trade basado en el historial real.
        Si no hay suficientes datos, retorna valores estimados a partir del backtest (ya ejecutado).
        """
        if self.analyzer is None or len(self.history) < 2:
            # Si no hay historial, se usa el promedio del backtest (que ya se ejecutó)
            # Pero como ensure_history ya lo ha hecho, esto no debería ocurrir.
            return {
                'elapsed': 0,
                'avg_interval': 0,
                'remaining_minutes': 0,
                'confidence': 0.0,
                'interval_ci': (0, 0),
                'historical_error': 0.0
            }

        last_time = self.get_last_trade_time()
        if last_time is None:
            return self._default_estimate()

        now = datetime.now()
        elapsed = (now - last_time).total_seconds() / 60

        # Usar la distribución real
        summary = self.analyzer.get_summary()
        mean_interval = summary.get('mean', 45)
        std_interval = summary.get('std', 15)
        p10 = summary.get('percentiles', {}).get('p10', 20)
        p90 = summary.get('percentiles', {}).get('p90', 70)

        remaining = max(0, mean_interval - elapsed)
        ci = (max(0, p10 - elapsed), max(0, p90 - elapsed))

        # Error histórico estimado
        hist_error = std_interval / mean_interval if mean_interval > 0 else 0.3
        confidence = 1.0 - min(hist_error, 0.9)

        return {
            'elapsed': elapsed,
            'avg_interval': mean_interval,
            'remaining_minutes': remaining,
            'confidence': confidence,
            'interval_ci': ci,
            'historical_error': hist_error
        }

    def _default_estimate(self):
        return {
            'elapsed': 0,
            'avg_interval': 45,
            'remaining_minutes': 45,
            'confidence': 0.5,
            'interval_ci': (10, 80),
            'historical_error': 0.3
        }
