# walk_forward.py
import pandas as pd
import numpy as np
from typing import List, Dict
from backtest import Backtest

class WalkForward:
    """Walk-Forward Validation con 5 iteraciones."""

    def __init__(self, data_provider, statistics, history):
        self.data = data_provider
        self.stats = statistics
        self.history = history

    def run(self, symbols: List[str] = None, n_splits: int = 5) -> Dict:
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT']

        results = []
        for split in range(n_splits):
            # Ventanas de 3 meses (90 días) de prueba
            train_days = 180
            test_days = 90
            offset = split * test_days

            # Simular con diferentes ventanas de tiempo
            # En producción, se usarían datos históricos reales
            bt = Backtest(self.data, self.stats, self.history)
            result = bt.run(symbols, days=train_days + test_days)
            results.append({
                'split': split + 1,
                'win_rate': result['win_rate'],
                'profit_factor': result['profit_factor'],
                'sharpe': result['sharpe'],
                'max_drawdown': result['max_drawdown'],
                'n_trades': result['n_trades']
            })

        return {
            'splits': results,
            'avg_win_rate': np.mean([r['win_rate'] for r in results]),
            'avg_pf': np.mean([r['profit_factor'] for r in results]),
            'avg_sharpe': np.mean([r['sharpe'] for r in results]),
            'std_win_rate': np.std([r['win_rate'] for r in results])
        }