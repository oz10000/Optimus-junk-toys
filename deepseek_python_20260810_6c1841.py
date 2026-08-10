# backtest.py
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from config import CONFIG
from decision_engine import DecisionEngine
from signal_generator import SignalGenerator
from position_manager import PositionManager
from indicators import Indicators

class Backtest:
    """Ejecuta backtesting completo del sistema."""

    def __init__(self, data_provider, statistics, history):
        self.data = data_provider
        self.stats = statistics
        self.history = history
        self.engine = DecisionEngine(data_provider, statistics, history)

    def run(self, symbols: List[str] = None, days: int = 90) -> Dict:
        """Ejecuta backtest para los activos dados."""
        if symbols is None:
            symbols = CONFIG.universe

        all_trades = []
        equity = []

        for sym in symbols:
            df = self.data.get_ohlcv(sym, timeframe='5m', limit=days * 288)
            if df is None or df.empty:
                continue

            trades = self._run_symbol(sym, df)
            all_trades.extend(trades)
            equity.extend([t['pnl_pct'] for t in trades])

        total_return = sum(equity)
        win_rate = len([t for t in all_trades if t['pnl_pct'] > 0]) / len(all_trades) if all_trades else 0
        pf = self._profit_factor(all_trades)
        sharpe = self._sharpe_ratio(equity)
        max_dd = self._max_drawdown(equity)

        return {
            'trades': all_trades,
            'total_return': total_return,
            'win_rate': win_rate,
            'profit_factor': pf,
            'sharpe': sharpe,
            'max_drawdown': max_dd,
            'n_trades': len(all_trades)
        }

    def _run_symbol(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        trades = []
        position = None

        for i in range(100, len(df)):
            slice_df = df.iloc[:i+1]
            decision = self.engine.evaluate(symbol, slice_df)
            if decision and position is None:
                # Abrir posición
                pos = PositionManager(
                    symbol, decision['direction'], decision['entry_price'],
                    decision['position_size'], decision['leverage']['recommended'],
                    decision['sl_price'], decision['tp_price'],
                    decision['atr'], decision['adx'],
                    decision['volatility'], decision['regime'],
                    trades
                )
                position = pos

            elif position is not None:
                current_price = df['close'].iloc[i]
                events = position.update(current_price)
                if events.get('events'):
                    trades.append({
                        'symbol': symbol,
                        'direction': position.direction,
                        'entry_price': position.entry_price,
                        'exit_price': current_price,
                        'pnl_pct': events['pnl_pct'],
                        'reason': events['events'][0] if events['events'] else 'unknown',
                        'timestamp': df.index[i]
                    })
                    position = None

        return trades

    @staticmethod
    def _profit_factor(trades: List[Dict]) -> float:
        wins = sum([t['pnl_pct'] for t in trades if t['pnl_pct'] > 0])
        losses = abs(sum([t['pnl_pct'] for t in trades if t['pnl_pct'] < 0]))
        return wins / losses if losses > 0 else np.inf

    @staticmethod
    def _sharpe_ratio(equity: List[float]) -> float:
        returns = pd.Series(equity)
        if returns.std() == 0:
            return 0.0
        return (returns.mean() / returns.std()) * np.sqrt(252 * 24 * 60 / 5)

    @staticmethod
    def _max_drawdown(equity: List[float]) -> float:
        if not equity:
            return 0.0
        peak = np.maximum.accumulate(equity)
        dd = (peak - np.array(equity)) / (peak + 1e-9)
        return float(dd.min()) if len(dd) > 0 else 0.0