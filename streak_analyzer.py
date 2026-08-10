# streak_analyzer.py
import numpy as np
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime

class StreakAnalyzer:
    """
    Análisis completo de rachas por múltiples dimensiones.
    """
    
    def __init__(self, history: List[Dict]):
        self.history = history
        self._compute_all_streaks()
    
    def _compute_all_streaks(self):
        """Calcula rachas por todas las dimensiones."""
        # Rachas generales
        self.general = self._compute_streak_sequence(self.history)
        
        # Rachas por activo
        self.by_asset = self._compute_by_dimension('symbol')
        
        # Rachas por horario
        self.by_hour = self._compute_by_hour()
        
        # Rachas por régimen
        self.by_regime = self._compute_by_dimension('regime')
        
        # Rachas por día
        self.by_weekday = self._compute_by_weekday()
    
    def _compute_streak_sequence(self, trades: List[Dict]) -> Dict:
        """Calcula rachas para una secuencia de trades."""
        if len(trades) < 2:
            return self._default_streak()
        
        # Identificar W/L
        results = ['W' if t.get('pnl_pct', 0) > 0 else 'L' for t in trades]
        
        # Rachas consecutivas
        current_streak = 1
        current_type = results[0]
        streaks = []
        
        for i in range(1, len(results)):
            if results[i] == results[i-1]:
                current_streak += 1
            else:
                streaks.append({'type': current_type, 'length': current_streak})
                current_type = results[i]
                current_streak = 1
        streaks.append({'type': current_type, 'length': current_streak})
        
        # Estadísticas de rachas
        win_streaks = [s['length'] for s in streaks if s['type'] == 'W']
        loss_streaks = [s['length'] for s in streaks if s['type'] == 'L']
        
        # Rachas activas
        current_active = streaks[-1] if streaks else None
        
        # Bloques WW, WL, LW, LL
        blocks = defaultdict(int)
        for i in range(0, len(results) - 1, 2):
            if i + 1 < len(results):
                block = results[i] + results[i+1]
                blocks[block] += 1
        
        total_blocks = sum(blocks.values())
        block_probs = {k: v / total_blocks for k, v in blocks.items()} if total_blocks > 0 else {}
        
        return {
            'streaks': streaks,
            'win_streaks': {
                'count': len(win_streaks),
                'max': max(win_streaks) if win_streaks else 0,
                'mean': np.mean(win_streaks) if win_streaks else 0,
                'current': current_active['length'] if current_active and current_active['type'] == 'W' else 0
            },
            'loss_streaks': {
                'count': len(loss_streaks),
                'max': max(loss_streaks) if loss_streaks else 0,
                'mean': np.mean(loss_streaks) if loss_streaks else 0,
                'current': current_active['length'] if current_active and current_active['type'] == 'L' else 0
            },
            'blocks': blocks,
            'block_probabilities': block_probs,
            'total_trades': len(results),
            'win_rate': results.count('W') / len(results) if results else 0
        }
    
    def _compute_by_dimension(self, key: str) -> Dict:
        """Calcula rachas agrupadas por una dimensión."""
        result = {}
        grouped = defaultdict(list)
        
        for t in self.history:
            dim = t.get(key, 'unknown')
            grouped[dim].append(t)
        
        for dim, trades in grouped.items():
            if len(trades) >= 2:
                result[dim] = self._compute_streak_sequence(trades)
            else:
                result[dim] = self._default_streak()
        
        return result
    
    def _compute_by_hour(self) -> Dict:
        """Calcula rachas por hora del día."""
        result = {}
        grouped = defaultdict(list)
        
        for t in self.history:
            ts = t.get('timestamp')
            if ts and isinstance(ts, datetime):
                hour = ts.hour
                grouped[hour].append(t)
        
        for hour, trades in grouped.items():
            if len(trades) >= 2:
                result[hour] = self._compute_streak_sequence(trades)
            else:
                result[hour] = self._default_streak()
        
        return result
    
    def _compute_by_weekday(self) -> Dict:
        """Calcula rachas por día de la semana."""
        result = {}
        grouped = defaultdict(list)
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        for t in self.history:
            ts = t.get('timestamp')
            if ts and isinstance(ts, datetime):
                wd = ts.weekday()
                grouped[wd].append(t)
        
        for wd, trades in grouped.items():
            if len(trades) >= 2:
                result[days[wd]] = self._compute_streak_sequence(trades)
            else:
                result[days[wd]] = self._default_streak()
        
        return result
    
    def _default_streak(self) -> Dict:
        """Valores por defecto para streak."""
        return {
            'streaks': [],
            'win_streaks': {'count': 0, 'max': 0, 'mean': 0, 'current': 0},
            'loss_streaks': {'count': 0, 'max': 0, 'mean': 0, 'current': 0},
            'blocks': {},
            'block_probabilities': {},
            'total_trades': 0,
            'win_rate': 0
        }
    
    def is_favored_by_streak(self, current_trade: Dict) -> Dict:
        """
        Determina si el trade actual está favorecido por la racha histórica.
        
        Returns:
            Dict con 'answer': 'SI'/'NO', 'explanation': str
        """
        # Obtener la racha actual
        general = self.general
        current_loss_streak = general['loss_streaks']['current']
        current_win_streak = general['win_streaks']['current']
        
        # Probabilidad de bloque
        block_probs = general.get('block_probabilities', {})
        ww_prob = block_probs.get('WW', 0.25)
        ll_prob = block_probs.get('LL', 0.25)
        
        # Determinar si está favorecido
        # Si venimos de una racha de pérdidas, y LL es baja, es favorable
        if current_loss_streak > 0:
            if ll_prob < 0.15:
                answer = 'SI'
                reason = f"Racha de {current_loss_streak} pérdidas consecutivas. Históricamente, LL ocurre solo {ll_prob*100:.1f}% de las veces → reversión probable."
            elif ll_prob < 0.30:
                answer = 'SI'
                reason = f"Racha de {current_loss_streak} pérdidas. LL ocurre {ll_prob*100:.1f}% → favorable pero con precaución."
            else:
                answer = 'NO'
                reason = f"Racha de {current_loss_streak} pérdidas. LL ocurre {ll_prob*100:.1f}% → no hay evidencia de reversión."
        
        # Si venimos de una racha de ganancias
        elif current_win_streak > 0:
            if ww_prob > 0.35:
                answer = 'SI'
                reason = f"Racha de {current_win_streak} ganancias. WW ocurre {ww_prob*100:.1f}% → momentum favorable."
            else:
                answer = 'NO'
                reason = f"Racha de {current_win_streak} ganancias. WW ocurre {ww_prob*100:.1f}% → posible agotamiento."
        
        else:
            answer = 'NEUTRAL'
            reason = "Sin racha activa significativa."
        
        return {
            'answer': answer,
            'explanation': reason,
            'current_loss_streak': current_loss_streak,
            'current_win_streak': current_win_streak,
            'ww_probability': ww_prob,
            'll_probability': ll_prob
        }
