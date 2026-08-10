# distribution_analyzer.py
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

class DistributionAnalyzer:
    """
    Analiza la distribución completa de intervalos entre trades.
    """
    
    def __init__(self, history: List[Dict]):
        self.history = history
        self._compute_distributions()
    
    def _compute_distributions(self):
        """Calcula todas las distribuciones."""
        if len(self.history) < 2:
            self._set_defaults()
            return
        
        timestamps = [t.get('timestamp') for t in self.history if t.get('timestamp')]
        if len(timestamps) < 2:
            self._set_defaults()
            return
        
        # Distribución de intervalos
        intervals = []
        for i in range(1, len(timestamps)):
            if isinstance(timestamps[i], datetime) and isinstance(timestamps[i-1], datetime):
                delta = (timestamps[i] - timestamps[i-1]).total_seconds() / 60
                if delta > 0:
                    intervals.append(delta)
        
        if len(intervals) == 0:
            self._set_defaults()
            return
        
        self.intervals = np.array(intervals)
        
        # Estadísticas básicas
        self.mean = np.mean(intervals)
        self.std = np.std(intervals)
        self.median = np.median(intervals)
        self.min_val = np.min(intervals)
        self.max_val = np.max(intervals)
        
        # Percentiles
        self.percentiles = {
            'p5': np.percentile(intervals, 5),
            'p10': np.percentile(intervals, 10),
            'p25': np.percentile(intervals, 25),
            'p50': np.percentile(intervals, 50),
            'p75': np.percentile(intervals, 75),
            'p90': np.percentile(intervals, 90),
            'p95': np.percentile(intervals, 95)
        }
        
        # Distribución por activo
        self.by_asset = self._compute_by_dimension('symbol')
        
        # Distribución por horario
        self.by_hour = self._compute_by_hour()
        
        # Distribución por régimen
        self.by_regime = self._compute_by_dimension('regime')
        
        # Distribución por día de la semana
        self.by_weekday = self._compute_by_weekday()
    
    def _compute_by_dimension(self, key: str) -> Dict:
        """Calcula distribución por una dimensión."""
        result = {}
        for t in self.history:
            val = t.get(key, 'unknown')
            if val not in result:
                result[val] = []
            # Necesitamos el timestamp siguiente para el intervalo
        # Reconstruir intervalos por dimensión
        dim_data = defaultdict(list)
        timestamps_by_dim = defaultdict(list)
        
        for t in self.history:
            dim = t.get(key, 'unknown')
            ts = t.get('timestamp')
            if ts:
                timestamps_by_dim[dim].append(ts)
        
        for dim, ts_list in timestamps_by_dim.items():
            if len(ts_list) < 2:
                continue
            for i in range(1, len(ts_list)):
                if isinstance(ts_list[i], datetime) and isinstance(ts_list[i-1], datetime):
                    delta = (ts_list[i] - ts_list[i-1]).total_seconds() / 60
                    if delta > 0:
                        dim_data[dim].append(delta)
        
        for dim, intervals in dim_data.items():
            if intervals:
                arr = np.array(intervals)
                result[dim] = {
                    'mean': np.mean(arr),
                    'std': np.std(arr),
                    'median': np.median(arr),
                    'count': len(arr),
                    'percentiles': {
                        'p10': np.percentile(arr, 10),
                        'p50': np.percentile(arr, 50),
                        'p90': np.percentile(arr, 90)
                    }
                }
        
        return result
    
    def _compute_by_hour(self) -> Dict:
        """Calcula distribución por hora del día."""
        result = {}
        timestamps_by_hour = defaultdict(list)
        
        for t in self.history:
            ts = t.get('timestamp')
            if ts and isinstance(ts, datetime):
                hour = ts.hour
                timestamps_by_hour[hour].append(ts)
        
        for hour, ts_list in timestamps_by_hour.items():
            if len(ts_list) < 2:
                continue
            intervals = []
            for i in range(1, len(ts_list)):
                delta = (ts_list[i] - ts_list[i-1]).total_seconds() / 60
                if delta > 0:
                    intervals.append(delta)
            if intervals:
                arr = np.array(intervals)
                result[hour] = {
                    'mean': np.mean(arr),
                    'std': np.std(arr),
                    'count': len(arr),
                    'frequency': len(ts_list)
                }
        
        return result
    
    def _compute_by_weekday(self) -> Dict:
        """Calcula distribución por día de la semana."""
        result = {}
        timestamps_by_day = defaultdict(list)
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        for t in self.history:
            ts = t.get('timestamp')
            if ts and isinstance(ts, datetime):
                wd = ts.weekday()
                timestamps_by_day[wd].append(ts)
        
        for wd, ts_list in timestamps_by_day.items():
            if len(ts_list) < 2:
                continue
            intervals = []
            for i in range(1, len(ts_list)):
                delta = (ts_list[i] - ts_list[i-1]).total_seconds() / 60
                if delta > 0:
                    intervals.append(delta)
            if intervals:
                arr = np.array(intervals)
                result[days[wd]] = {
                    'mean': np.mean(arr),
                    'std': np.std(arr),
                    'count': len(arr),
                    'frequency': len(ts_list)
                }
        
        return result
    
    def _set_defaults(self):
        """Valores por defecto."""
        self.intervals = np.array([])
        self.mean = 45.0
        self.std = 15.0
        self.median = 40.0
        self.min_val = 5.0
        self.max_val = 120.0
        self.percentiles = {'p5': 10, 'p10': 15, 'p25': 25, 'p50': 40, 'p75': 55, 'p90': 70, 'p95': 85}
        self.by_asset = {}
        self.by_hour = {}
        self.by_regime = {}
        self.by_weekday = {}
    
    def get_summary(self) -> Dict:
        """Retorna un resumen completo de la distribución."""
        return {
            'mean': round(self.mean, 2),
            'std': round(self.std, 2),
            'median': round(self.median, 2),
            'min': round(self.min_val, 2),
            'max': round(self.max_val, 2),
            'percentiles': {k: round(v, 2) for k, v in self.percentiles.items()},
            'by_asset': self.by_asset,
            'by_hour': self.by_hour,
            'by_regime': self.by_regime,
            'by_weekday': self.by_weekday,
            'n_intervals': len(self.intervals)
        }
