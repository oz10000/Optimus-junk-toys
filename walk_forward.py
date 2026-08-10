# walk_forward.py
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta
from backtest import Backtest

class WalkForward:
    def __init__(self, data_provider, statistics, history):
        self.data = data_provider
        self.stats = statistics
        self.history = history

    def run(self, symbols: List[str] = None, train_days: int = 180, 
            test_days: int = 90, n_splits: int = 5) -> Dict:
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT']
        results = []
        end_date = datetime.now()
        for split in range(n_splits):
            test_end = end_date - timedelta(days=split * test_days)
            test_start = test_end - timedelta(days=test_days)
            train_start = test_start - timedelta(days=train_days)
            bt = Backtest(self.data, None)  # sin decision engine, se usa el interno
            # Nota: en una implementación real se usaría el decision engine con entrenamiento en train_start
            # Simulación simplificada: ejecutamos backtest en el período test_start-test_end
            result = bt.run(symbols, test_start, test_end, timeframe='5m')
            results.append({
                'split': split + 1,
                'train_start': train_start.isoformat(),
                'train_end': test_start.isoformat(),
                'test_start': test_start.isoformat(),
                'test_end': test_end.isoformat(),
                'win_rate': result['metrics'].get('win_rate', 0),
                'profit_factor': result['metrics'].get('profit_factor', 0),
                'sharpe': result['metrics'].get('sharpe', 0),
                'max_drawdown': result['metrics'].get('max_drawdown', 0),
                'n_trades': result['n_trades']
            })
        return {
            'splits': results,
            'avg_win_rate': np.mean([r['win_rate'] for r in results]),
            'avg_pf': np.mean([r['profit_factor'] for r in results]),
            'avg_sharpe': np.mean([r['sharpe'] for r in results]),
            'std_win_rate': np.std([r['win_rate'] for r in results]),
            'consistency_score': 1.0 - np.std([r['win_rate'] for r in results]),
            'n_splits': n_splits,
            'train_days': train_days,
            'test_days': test_days
        }
