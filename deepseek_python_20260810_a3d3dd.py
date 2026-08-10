# monte_carlo.py
import numpy as np
from typing import List, Dict

class MonteCarlo:
    """Monte Carlo Simulation (1000 iteraciones) sobre los trades."""

    @staticmethod
    def run(trades: List[Dict], n_simulations: int = 1000) -> Dict:
        if not trades:
            return {'final_capital': [], 'drawdown': [], 'sharpe': []}

        pnls = [t['pnl_pct'] for t in trades]
        initial_capital = 10000.0

        final_capitals = []
        max_drawdowns = []
        sharpes = []

        for _ in range(n_simulations):
            sampled = np.random.choice(pnls, size=len(pnls), replace=True)
            equity = np.cumsum(sampled)
            final_cap = initial_capital * (1 + equity[-1] / 100)
            final_capitals.append(final_cap)

            # Drawdown
            peak = np.maximum.accumulate(equity)
            dd = (peak - equity) / (peak + 1e-9)
            max_drawdowns.append(dd.min())

            # Sharpe
            returns = pd.Series(equity).pct_change().dropna()
            sharpes.append(returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0)

        return {
            'mean_final_capital': np.mean(final_capitals),
            'std_final_capital': np.std(final_capitals),
            'percentile_5': np.percentile(final_capitals, 5),
            'percentile_95': np.percentile(final_capitals, 95),
            'mean_max_dd': np.mean(max_drawdowns),
            'mean_sharpe': np.mean(sharpes),
            'ruin_prob': np.mean(np.array(final_capitals) < initial_capital * 0.5)
        }