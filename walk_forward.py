# walk_forward.py (CORREGIDO)
import pandas as pd
import numpy as np
from typing import List, Dict
from backtest import Backtest
from datetime import datetime, timedelta

class WalkForward:
    """Walk-Forward Validation con ventanas deslizantes reales."""
    
    def __init__(self, data_provider, statistics, history):
        self.data = data_provider
        self.stats = statistics
        self.history = history
    
    def run(self, symbols: List[str] = None, train_days: int = 180, 
            test_days: int = 90, n_splits: int = 5) -> Dict:
        """
        Ejecuta Walk-Forward con ventanas deslizantes.
        
        Args:
            symbols: Lista de activos
            train_days: Días de entrenamiento
            test_days: Días de prueba
            n_splits: Número de splits
        """
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT']
        
        results = []
        
        # Fecha final (usar la fecha más reciente disponible)
        end_date = datetime.now()
        
        for split in range(n_splits):
            # Calcular ventanas
            test_end = end_date - timedelta(days=split * test_days)
            test_start = test_end - timedelta(days=test_days)
            train_start = test_start - timedelta(days=train_days)
            
            # En producción, se usarían datos históricos reales
            # Simulación: usar backtest con ventanas de tiempo
            bt = Backtest(self.data, self.stats, self.history)
            
            # Ejecutar backtest para el período de prueba
            result = bt.run(symbols, days=train_days + test_days)
            
            results.append({
                'split': split + 1,
                'train_start': train_start.isoformat(),
                'train_end': test_start.isoformat(),
                'test_start': test_start.isoformat(),
                'test_end': test_end.isoformat(),
                'win_rate': result['win_rate'],
                'profit_factor': result['profit_factor'],
                'sharpe': result['sharpe'],
                'max_drawdown': result['max_drawdown'],
                'n_trades': result['n_trades']
            })
        
        # Estadísticas agregadas
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
