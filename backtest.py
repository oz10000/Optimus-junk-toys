# backtest.py - VERSIÓN COMPLETA SIN TRADES FICTICIOS
import numpy as np
import pandas as pd
from typing import List, Dict
from datetime import datetime, timedelta
from data import DataProvider
from decision_engine import DecisionEngine
from config import CONFIG


class Backtest:
    def __init__(self, data_provider: DataProvider, decision_engine: DecisionEngine):
        self.data = data_provider
        self.engine = decision_engine
        self.trades = []

    def run(self, symbols: List[str], start_date: datetime, end_date: datetime,
            timeframe: str = '5m') -> Dict:
        self.trades = []

        for symbol in symbols:
            df = self.data.get_ohlcv(symbol, timeframe, limit=10000)
            if df is None or df.empty:
                continue

            df = df[(df.index >= start_date) & (df.index <= end_date)]
            if len(df) < 50:
                continue

            position = None

            # Evaluar CADA vela
            for i in range(50, len(df)):
                current_time = df.index[i]
                current_price = df.iloc[i]['close']
                data_slice = df.iloc[:i+1]

                if position is None:
                    decision = self.engine.evaluate(symbol, data_slice)
                    if decision is not None and decision.get('action') != 'HOLD':
                        direction = decision.get('direction', 'LONG')
                        entry_price = current_price
                        sl_pct = decision.get('sl_pct', 0.016)
                        tp_pct = decision.get('tp_pct', 0.038)

                        position = {
                            'symbol': symbol,
                            'direction': direction,
                            'entry_price': entry_price,
                            'entry_time': current_time,
                            'sl_pct': sl_pct,
                            'tp_pct': tp_pct,
                            'regime': decision.get('regime', 'Normal'),
                            'volatility': decision.get('volatility', 0.01),
                            'sl_price': entry_price * (1 - sl_pct) if direction == 'LONG' else entry_price * (1 + sl_pct),
                            'tp_price': entry_price * (1 + tp_pct) if direction == 'LONG' else entry_price * (1 - tp_pct),
                            'highest': entry_price,
                            'lowest': entry_price,
                            'trailing_active': False,
                            'trailing_stop': decision.get('trailing_distance', 0.006),
                            'trailing_activation': decision.get('trailing_activation', 0.012),
                            'be_trigger': decision.get('be_trigger', 0.0035),
                            'be_applied': False,
                        }
                else:
                    # Actualizar trailing stop
                    if position['direction'] == 'LONG':
                        if current_price > position['highest']:
                            position['highest'] = current_price
                            if not position['trailing_active'] and current_price > position['entry_price'] * (1 + position['trailing_activation']):
                                position['trailing_active'] = True
                            if position['trailing_active']:
                                new_sl = current_price * (1 - position['trailing_stop'])
                                if new_sl > position['sl_price']:
                                    position['sl_price'] = new_sl
                            if not position['be_applied'] and current_price > position['entry_price'] * (1 + position['be_trigger']):
                                position['sl_price'] = position['entry_price']
                                position['be_applied'] = True
                    else:  # SHORT
                        if current_price < position['lowest']:
                            position['lowest'] = current_price
                            if not position['trailing_active'] and current_price < position['entry_price'] * (1 - position['trailing_activation']):
                                position['trailing_active'] = True
                            if position['trailing_active']:
                                new_sl = current_price * (1 + position['trailing_stop'])
                                if new_sl < position['sl_price']:
                                    position['sl_price'] = new_sl
                            if not position['be_applied'] and current_price < position['entry_price'] * (1 - position['be_trigger']):
                                position['sl_price'] = position['entry_price']
                                position['be_applied'] = True

                    # Verificar salida
                    exit_price = None
                    exit_reason = None
                    if position['direction'] == 'LONG':
                        if current_price <= position['sl_price']:
                            exit_price = position['sl_price']
                            exit_reason = 'Stop Loss'
                        elif current_price >= position['tp_price']:
                            exit_price = position['tp_price']
                            exit_reason = 'Take Profit'
                    else:
                        if current_price >= position['sl_price']:
                            exit_price = position['sl_price']
                            exit_reason = 'Stop Loss'
                        elif current_price <= position['tp_price']:
                            exit_price = position['tp_price']
                            exit_reason = 'Take Profit'

                    if exit_price is not None:
                        pnl_pct = (exit_price - position['entry_price']) / position['entry_price']
                        if position['direction'] == 'SHORT':
                            pnl_pct = -pnl_pct

                        duration_minutes = (current_time - position['entry_time']).total_seconds() / 60

                        self.trades.append({
                            'symbol': position['symbol'],
                            'timestamp': position['entry_time'],
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'direction': position['direction'],
                            'pnl_pct': pnl_pct,
                            'duration_minutes': duration_minutes,
                            'regime': position['regime'],
                            'volatility': position['volatility'],
                            'trailing_stop_used': position['trailing_stop'],
                            'break_even_applied': position['be_applied'],
                            'reason_exit': exit_reason,
                        })
                        position = None

        # NO crear trades ficticios
        return {
            'trades': self.trades,
            'n_trades': len(self.trades),
        }
