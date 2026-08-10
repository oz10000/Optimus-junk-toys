# statistics.py
import pandas as pd
import numpy as np
from typing import List, Dict
from collections import defaultdict

class StatisticsEngine:
    """Motor de estadísticas históricas y análisis por activo."""

    def __init__(self):
        self.trades = []
        self.metrics = {}

    def add_trade(self, trade: Dict):
        self.trades.append(trade)

    def get_metrics(self, symbol: str = None) -> Dict:
        """Calcula métricas para un activo o para todos."""
        filtered = [t for t in self.trades if symbol is None or t.get('symbol') == symbol]
        if not filtered:
            return {}

        pnls = [t['pnl_pct'] for t in filtered]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        n = len(pnls)
        win_rate = len(wins) / n if n > 0 else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        profit_factor = (sum(wins) / abs(sum(losses))) if losses else np.inf
        expectancy = win_rate * avg_win - (1 - win_rate) * avg_loss
        max_dd = self._max_drawdown(pnls)

        return {
            'n_trades': n,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_dd,
            'total_return': sum(pnls),
        }

    @staticmethod
    def _max_drawdown(pnls: List[float]) -> float:
        equity = np.cumsum(pnls)
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / (peak + 1e-9)
        return float(dd.min()) if len(dd) > 0 else 0.0
