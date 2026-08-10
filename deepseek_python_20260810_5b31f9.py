# performance.py
from typing import List, Dict
from metrics import Metrics
from collections import defaultdict

class Performance:
    """Análisis de rendimiento por activo, horario, día y régimen."""

    @staticmethod
    def by_asset(trades: List[Dict]) -> Dict:
        by_asset = defaultdict(list)
        for t in trades:
            by_asset[t.get('symbol', 'unknown')].append(t)
        return {sym: Metrics.compute(trades) for sym, trades in by_asset.items()}

    @staticmethod
    def by_hour(trades: List[Dict]) -> Dict:
        by_hour = defaultdict(list)
        for t in trades:
            hour = t.get('timestamp', pd.Timestamp.now()).hour
            by_hour[hour].append(t)
        return {h: Metrics.compute(trades) for h, trades in by_hour.items()}

    @staticmethod
    def by_weekday(trades: List[Dict]) -> Dict:
        by_weekday = defaultdict(list)
        for t in trades:
            wd = t.get('timestamp', pd.Timestamp.now()).weekday()
            by_weekday[wd].append(t)
        return {wd: Metrics.compute(trades) for wd, trades in by_weekday.items()}

    @staticmethod
    def by_regime(trades: List[Dict]) -> Dict:
        by_regime = defaultdict(list)
        for t in trades:
            regime = t.get('regime', 'Normal')
            by_regime[regime].append(t)
        return {r: Metrics.compute(trades) for r, trades in by_regime.items()}