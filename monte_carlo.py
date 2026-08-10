# monte_carlo.py
import numpy as np
import pandas as pd
from typing import List, Dict

class MonteCarlo:
    @staticmethod
    def run(trades: List[Dict], n_simulations: int = 1000,
            initial_capital: float = 10000.0) -> Dict:
        if not trades:
            return MonteCarlo._empty_result()
        returns = np.array([t.get('pnl_pct', 0.0) for t in trades])
        if np.all(returns == 0.0):
            returns = np.array([
                (t.get('exit_price', 0) / t.get('entry_price', 1) - 1)
                if t.get('entry_price', 0) > 0 else 0.0
                for t in trades
            ])
        n = len(returns)
        if n == 0:
            return MonteCarlo._empty_result()
        sim_returns = np.random.choice(returns, size=(n_simulations, n), replace=True)
        equity_multipliers = np.cumprod(1 + sim_returns, axis=1)
        final_capitals = initial_capital * equity_multipliers[:, -1]
        peaks = np.maximum.accumulate(equity_multipliers, axis=1)
        drawdowns = (peaks - equity_multipliers) / (peaks + 1e-9)
        max_dd_per_sim = np.max(drawdowns, axis=1)
        sim_means = np.mean(sim_returns, axis=1)
        sim_stds = np.std(sim_returns, axis=1)
        sharpe_sim = sim_means / (sim_stds + 1e-9) * np.sqrt(n)
        min_equity = np.min(equity_multipliers, axis=1)
        ruin_prob = np.mean(min_equity < 0.5)
        return {
            'mean_final_capital': np.mean(final_capitals),
            'median_final_capital': np.median(final_capitals),
            'percentile_5': np.percentile(final_capitals, 5),
            'percentile_95': np.percentile(final_capitals, 95),
            'mean_max_dd': np.mean(max_dd_per_sim),
            'mean_sharpe': np.mean(sharpe_sim),
            'ruin_prob': ruin_prob,
            'all_final_capitals': final_capitals.tolist(),
            'n_simulations': n_simulations,
            'n_trades_used': n
        }
    @staticmethod
    def _empty_result() -> Dict:
        return {
            'mean_final_capital': 0.0,
            'median_final_capital': 0.0,
            'percentile_5': 0.0,
            'percentile_95': 0.0,
            'mean_max_dd': 0.0,
            'mean_sharpe': 0.0,
            'ruin_prob': 0.0,
            'all_final_capitals': [],
            'n_simulations': 0,
            'n_trades_used': 0
        }
