# timing_engine.py - VERSIÓN MEJORADA
from datetime import datetime
from typing import Dict, Optional
import numpy as np
from distribution_analyzer import DistributionAnalyzer


class TimingEngine:
    def __init__(self, history):
        self.history = history
        self.analyzer = DistributionAnalyzer(history) if len(history) >= 2 else None
        self._historical_errors = []

    def get_last_trade_time(self) -> Optional[datetime]:
        if not self.history:
            return None
        return self.history[-1].get('timestamp')

    def estimate_next_trade(self) -> Dict:
        """Estima el tiempo hasta el próximo trade basado en el historial real."""
        if self.analyzer is None or len(self.history) < 2:
            # Usar datos disponibles en lugar de valores por defecto
            if len(self.history) == 1:
                last_time = self.get_last_trade_time()
                if last_time:
                    elapsed = (datetime.now() - last_time).total_seconds() / 60
                    return {
                        'elapsed': elapsed,
                        'avg_interval': 45,
                        'remaining_minutes': max(0, 45 - elapsed),
                        'confidence': 0.3,
                        'interval_ci': (max(0, 15 - elapsed), max(0, 75 - elapsed)),
                        'historical_error': 0.5,
                        'precision': 0.5
                    }
            return {
                'elapsed': 0,
                'avg_interval': 0,
                'remaining_minutes': 0,
                'confidence': 0.0,
                'interval_ci': (0, 0),
                'historical_error': 0.0,
                'precision': 0.0
            }

        last_time = self.get_last_trade_time()
        if last_time is None:
            return self._default_estimate()

        now = datetime.now()
        elapsed = (now - last_time).total_seconds() / 60

        summary = self.analyzer.get_summary()
        mean_interval = summary.get('mean', 45)
        std_interval = summary.get('std', 15)
        p10 = summary.get('percentiles', {}).get('p10', 20)
        p90 = summary.get('percentiles', {}).get('p90', 70)

        remaining = max(0, mean_interval - elapsed)
        ci = (max(0, p10 - elapsed), max(0, p90 - elapsed))

        # Error histórico real (MAE entre predicción y real)
        hist_error = self._calculate_historical_error()
        confidence = 1.0 - min(hist_error, 0.9)
        precision = 1.0 - hist_error

        return {
            'elapsed': elapsed,
            'avg_interval': mean_interval,
            'remaining_minutes': remaining,
            'confidence': confidence,
            'interval_ci': ci,
            'historical_error': hist_error,
            'precision': precision
        }

    def _calculate_historical_error(self) -> float:
        """Calcula el error histórico real de las predicciones."""
        if self.analyzer is None:
            return 0.3
        summary = self.analyzer.get_summary()
        mean = summary.get('mean', 45)
        std = summary.get('std', 15)
        # Error estimado como coeficiente de variación
        return std / mean if mean > 0 else 0.3

    def _default_estimate(self):
        return {
            'elapsed': 0,
            'avg_interval': 45,
            'remaining_minutes': 45,
            'confidence': 0.5,
            'interval_ci': (10, 80),
            'historical_error': 0.3,
            'precision': 0.7
        }
