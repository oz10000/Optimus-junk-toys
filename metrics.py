# metrics.py
import numpy as np
from typing import List, Dict

class Metrics:
    """Calcula todas las métricas de rendimiento."""

    @staticmethod
    def compute(trades: List[Dict]) -> Dict:
        if not trades:
            return {}

        pnls = [t['pnl_pct'] for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        n = len(pnls)

        win_rate = len(wins) / n if n > 0 else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        pf = sum(wins) / abs(sum(losses)) if losses else np.inf
        expectancy = win_rate * avg_win - (1 - win_rate) * avg_loss

        # Sharpe
        returns = pd.Series(pnls)
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        # Sortino
        downside = returns[returns < 0]
        sortino = returns.mean() / downside.std() * np.sqrt(252) if downside.std() > 0 else 0

        # Drawdown
        equity = np.cumsum(pnls)
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / (peak + 1e-9)
        max_dd = dd.min()
        avg_dd = dd.mean()

        # Calmar
        calmar = (equity[-1] / 100) / abs(max_dd) if max_dd != 0 else 0

        return {
            'win_rate': win_rate,
            'profit_factor': pf,
            'expectancy': expectancy,
            'sharpe': sharpe,
            'sortino': sortino,
            'calmar': calmar,
            'max_drawdown': max_dd,
            'avg_drawdown': avg_dd,
            'total_return': equity[-1],
            'n_trades': n,
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
