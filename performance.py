# performance.py
import numpy as np
import pandas as pd
from typing import List, Dict
from collections import defaultdict
from metrics import Metrics

class Performance:
    @staticmethod
    def by_asset(trades: List[Dict]) -> Dict[str, Dict]:
        if not trades:
            return {}
        grouped = defaultdict(list)
        for t in trades:
            symbol = t.get('symbol', 'unknown')
            grouped[symbol].append(t)
        result = {}
        for symbol, group in grouped.items():
            result[symbol] = Metrics.compute(group)
        return result

    @staticmethod
    def by_hour(trades: List[Dict]) -> Dict[int, Dict]:
        if not trades:
            return {}
        grouped = defaultdict(list)
        for t in trades:
            ts = t.get('timestamp')
            if ts is not None and hasattr(ts, 'hour'):
                grouped[ts.hour].append(t)
        result = {}
        for hour, group in grouped.items():
            result[hour] = Metrics.compute(group)
        return result

    @staticmethod
    def by_weekday(trades: List[Dict]) -> Dict[str, Dict]:
        if not trades:
            return {}
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        grouped = defaultdict(list)
        for t in trades:
            ts = t.get('timestamp')
            if ts is not None and hasattr(ts, 'weekday'):
                grouped[days[ts.weekday()]].append(t)
        result = {}
        for day, group in grouped.items():
            result[day] = Metrics.compute(group)
        return result

    @staticmethod
    def by_regime(trades: List[Dict]) -> Dict[str, Dict]:
        if not trades:
            return {}
        grouped = defaultdict(list)
        for t in trades:
            regime = t.get('regime', 'unknown')
            grouped[regime].append(t)
        result = {}
        for regime, group in grouped.items():
            result[regime] = Metrics.compute(group)
        return result
