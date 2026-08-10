# streak_engine.py
from typing import List, Dict
from collections import defaultdict
import numpy as np

class StreakEngine:
    """Estudia rachas de trades y ajusta riesgo dinámicamente."""

    def __init__(self, history: List[Dict]):
        self.history = history
        self.streaks = self._compute_streaks()

    def _compute_streaks(self) -> Dict:
        """Calcula rachas WW, WL, LW, LL."""
        if len(self.history) < 2:
            return {}

        streaks = defaultdict(int)
        for i in range(0, len(self.history) - 1, 2):
            r1 = self.history[i].get('pnl_pct', 0)
            r2 = self.history[i+1].get('pnl_pct', 0) if i+1 < len(self.history) else 0
            key = ('W' if r1 > 0 else 'L') + ('W' if r2 > 0 else 'L')
            streaks[key] += 1

        return streaks

    def get_block_probability(self) -> Dict:
        """Probabilidad de cada tipo de bloque."""
        total = sum(self.streaks.values())
        if total == 0:
            return {'WW': 0, 'WL': 0, 'LW': 0, 'LL': 0}
        return {k: v / total for k, v in self.streaks.items()}

    def get_position_size_multiplier(self) -> float:
        """Ajusta tamaño según última racha."""
        probs = self.get_block_probability()
        ww = probs.get('WW', 0.5)
        ll = probs.get('LL', 0.1)
        base = 1.0
        if ww > 0.6:
            base *= 1.10  # WW bonus
        if ll > 0.2:
            base *= 0.80  # LL penalty
        return min(1.5, max(0.5, base))

    def get_max_streak(self) -> int:
        """Máxima racha de pérdidas consecutivas."""
        max_loss = 0
        current = 0
        for t in self.history:
            if t.get('pnl_pct', 0) < 0:
                current += 1
                max_loss = max(max_loss, current)
            else:
                current = 0
        return max_loss