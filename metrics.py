# metrics.py
import numpy as np
import pandas as pd
from typing import List, Dict

class Metrics:
    @staticmethod
    def compute(trades: List[Dict]) -> Dict:
        if not trades:
            return Metrics._empty_metrics()
        returns = np.array([t.get('pnl_pct', 0.0) for t in trades])
        if np.all(returns == 0.0):
            returns = np.array([
                (t.get('exit_price', 0) / t.get('entry_price', 1) - 1)
                if t.get('entry_price', 0) > 0 else 0.0
                for t in trades
            ])
        n = len(returns)
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        n_wins = len(wins)
        n_losses = len(losses)
        win_rate = n_wins / n if n > 0 else 0.0
        total_gain = wins.sum() if n_wins > 0 else 0.0
        total_loss = abs(losses.sum()) if n_losses > 0 else 1e-9
        profit_factor = total_gain / total_loss if total_loss != 0 else float('inf')
        total_return = returns.sum() * 100
        avg_return = returns.mean() * 100 if n > 0 else 0.0
        std_return = returns.std() * 100 if n > 0 else 0.0
        if std_return > 0:
            sharpe = (avg_return / std_return) * np.sqrt(252)
        else:
            sharpe = 0.0
        downside = returns[returns < 0]
        if len(downside) > 0 and downside.std() > 0:
            sortino = (avg_return / (downside.std() * 100)) * np.sqrt(252)
        else:
            sortino = 0.0
        equity = np.cumsum(returns)
        peak = np.maximum.accumulate(equity)
        drawdown = (peak - equity) / (np.abs(peak) + 1e-9)
        max_drawdown = drawdown.max() if len(drawdown) > 0 else 0.0
        calmar = (total_return / 100) / (max_drawdown + 1e-9) if max_drawdown > 0 else 0.0
        expectancy = avg_return
        avg_win = wins.mean() * 100 if n_wins > 0 else 0.0
        avg_loss = losses.mean() * 100 if n_losses > 0 else 0.0
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        return {
            'n_trades': n,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'avg_return': avg_return,
            'std_return': std_return,
            'sharpe': sharpe,
            'sortino': sortino,
            'max_drawdown': max_drawdown,
            'calmar': calmar,
            'expectancy': expectancy,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio
        }
    @staticmethod
    def _empty_metrics() -> Dict:
        return {
            'n_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'total_return': 0.0,
            'avg_return': 0.0,
            'std_return': 0.0,
            'sharpe': 0.0,
            'sortino': 0.0,
            'max_drawdown': 0.0,
            'calmar': 0.0,
            'expectancy': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'win_loss_ratio': 0.0
        }
