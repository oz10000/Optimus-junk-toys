# temporal_confidence.py
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

class TemporalConfidence:
    def __init__(self, history: List[Dict]):
        self.history = history
        self._compute_metrics()
    
    def _compute_metrics(self):
        if len(self.history) < 2:
            self._set_defaults()
            return
        timestamps = [t.get('timestamp') for t in self.history if t.get('timestamp')]
        if len(timestamps) < 2:
            self._set_defaults()
            return
        intervals = []
        for i in range(1, len(timestamps)):
            if isinstance(timestamps[i], datetime) and isinstance(timestamps[i-1], datetime):
                delta = (timestamps[i] - timestamps[i-1]).total_seconds() / 60
                if delta > 0:
                    intervals.append(delta)
        if len(intervals) < 2:
            self._set_defaults()
            return
        self.intervals = np.array(intervals)
        self.mean_interval = np.mean(intervals)
        self.std_interval = np.std(intervals)
        self.median_interval = np.median(intervals)
        self.percentiles = {
            'p10': np.percentile(intervals, 10),
            'p25': np.percentile(intervals, 25),
            'p50': np.percentile(intervals, 50),
            'p75': np.percentile(intervals, 75),
            'p90': np.percentile(intervals, 90)
        }
        self.historical_error = self.std_interval / self.mean_interval if self.mean_interval > 0 else 1.0
        self.historical_accuracy = 1.0 - self.historical_error
        self.historical_accuracy = max(0, min(1, self.historical_accuracy))
        days = (timestamps[-1] - timestamps[0]).total_seconds() / 86400 if len(timestamps) > 1 else 1
        self.frequency = len(timestamps) / max(days, 1)
    
    def _set_defaults(self):
        self.intervals = np.array([])
        self.mean_interval = 45.0
        self.std_interval = 15.0
        self.median_interval = 40.0
        self.percentiles = {'p10': 20, 'p25': 30, 'p50': 40, 'p75': 55, 'p90': 70}
        self.historical_error = 0.3
        self.historical_accuracy = 0.7
        self.frequency = 1.2
    
    def compute_confidence(self, last_trade_time: Optional[datetime], 
                          current_time: datetime = None) -> Dict:
        if current_time is None:
            current_time = datetime.now()
        if last_trade_time is None:
            return {
                'score': 0.0,
                'level': 'Sin datos',
                'components': {},
                'interpretation': 'No hay historial de trades suficiente'
            }
        elapsed = (current_time - last_trade_time).total_seconds() / 60
        remaining = max(0, self.mean_interval - elapsed)
        confidence_interval = (
            max(0, self.percentiles['p10'] - elapsed),
            max(0, self.percentiles['p90'] - elapsed)
        )
        consistency = 1.0 - min(abs(elapsed - self.mean_interval) / self.mean_interval, 1.0) if self.mean_interval > 0 else 0.5
        accuracy = self.historical_accuracy
        error_score = 1.0 - min(self.historical_error, 1.0)
        freq_score = min(self.frequency / 3.0, 1.0)
        score = 0.35 * consistency + 0.25 * accuracy + 0.25 * error_score + 0.15 * freq_score
        if score >= 0.8:
            level = 'Alta'
        elif score >= 0.6:
            level = 'Media-Alta'
        elif score >= 0.4:
            level = 'Media'
        elif score >= 0.2:
            level = 'Media-Baja'
        else:
            level = 'Baja'
        return {
            'score': round(score, 3),
            'level': level,
            'components': {
                'consistency': round(consistency, 3),
                'historical_accuracy': round(accuracy, 3),
                'historical_error': round(error_score, 3),
                'frequency': round(freq_score, 3)
            },
            'metrics': {
                'elapsed_minutes': round(elapsed, 1),
                'remaining_minutes': round(remaining, 1),
                'mean_interval': round(self.mean_interval, 1),
                'std_interval': round(self.std_interval, 1),
                'confidence_interval': (round(confidence_interval[0], 1), round(confidence_interval[1], 1)),
                'historical_error_pct': round(self.historical_error * 100, 1),
                'frequency_per_day': round(self.frequency, 2)
            },
            'interpretation': f"Confianza {level}: {score*100:.1f}%"
        }
