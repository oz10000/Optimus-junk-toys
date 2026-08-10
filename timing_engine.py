# timing_engine.py
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class TimingEngine:
    """Estima tiempos entre trades y ventanas óptimas."""

    def __init__(self, history: List[Dict]):
        self.history = history

    def get_avg_interval(self, symbol: str = None) -> float:
        """Intervalo promedio entre trades (minutos)."""
        filtered = [t for t in self.history if symbol is None or t.get('symbol') == symbol]
        if len(filtered) < 2:
            return 45.0
        timestamps = [t['timestamp'] for t in filtered]
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() / 60
                     for i in range(len(timestamps)-1)]
        return np.mean(intervals) if intervals else 45.0

    def get_last_trade_time(self) -> Optional[datetime]:
        """Timestamp del último trade."""
        if not self.history:
            return None
        return self.history[-1].get('timestamp')

    def estimate_next_trade(self, symbol: str = None) -> Dict:
        """Estima tiempo restante hasta el próximo trade."""
        avg_interval = self.get_avg_interval(symbol)
        last_time = self.get_last_trade_time()
        if last_time is None:
            return {'remaining_minutes': avg_interval, 'confidence': 0.5}

        elapsed = (datetime.now() - last_time).total_seconds() / 60
        remaining = max(0, avg_interval - elapsed)
        confidence = 1 - (elapsed / avg_interval) if avg_interval > 0 else 0.5
        return {
            'remaining_minutes': remaining,
            'confidence': min(1, max(0, confidence)),
            'avg_interval': avg_interval,
            'elapsed': elapsed
        }

    def get_optimal_hours(self) -> List[tuple]:
        """Ventanas horarias con mayor frecuencia de trades."""
        if not self.history:
            return [(10, 12)]
        hours = [t['timestamp'].hour for t in self.history]
        counts = {}
        for h in hours:
            counts[h] = counts.get(h, 0) + 1
        sorted_hours = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        best = sorted_hours[:2]
        return [(b[0], b[0]+2) for b in best]
