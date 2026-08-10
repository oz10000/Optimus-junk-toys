# position_manager.py
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from config import CONFIG
from trailing_engine import TrailingEngine
from break_even_engine import BreakEvenEngine

class PositionManager:
    """Gestiona una posición activa."""

    def __init__(self, symbol: str, direction: str, entry_price: float,
                 size: float, leverage: int, sl_price: float, tp_price: float,
                 atr: float, adx: float, volatility: float, regime: str, history: list):
        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.size = size
        self.leverage = leverage
        self.sl_price = sl_price
        self.tp_price = tp_price
        self.atr = atr
        self.adx = adx
        self.volatility = volatility
        self.regime = regime
        self.history = history
        self.entry_time = datetime.now()
        self.trailing_active = False
        self.trailing_sl = None
        self.be_activated = False
        self.be_price = None

        # Calcular Break Even
        self.be_data = BreakEvenEngine.select_best(
            entry_price, atr, volatility, history
        )
        self.be_trigger = self.be_data['trigger']

        # Calcular Trailing
        self.trailing_data = TrailingEngine.compute(
            entry_price, atr, adx, volatility, regime, self.be_trigger
        )

    def update(self, current_price: float) -> Dict:
        """Actualiza la posición y retorna eventos de salida."""
        pnl_pct = (current_price - self.entry_price) / self.entry_price
        pnl_pct *= self.leverage

        if self.direction == 'Long':
            pnl_pct *= 1
        else:
            pnl_pct *= -1

        events = {'price': current_price, 'pnl_pct': pnl_pct, 'events': []}

        # Verificar SL
        if self.direction == 'Long' and current_price <= self.sl_price:
            events['events'].append('stop_loss')
            return events
        if self.direction == 'Short' and current_price >= self.sl_price:
            events['events'].append('stop_loss')
            return events

        # Verificar TP
        if self.direction == 'Long' and current_price >= self.tp_price:
            events['events'].append('take_profit')
            return events
        if self.direction == 'Short' and current_price <= self.tp_price:
            events['events'].append('take_profit')
            return events

        # Break Even
        if not self.be_activated:
            if self.direction == 'Long' and current_price >= self.entry_price * (1 + self.be_trigger):
                self.be_activated = True
                self.be_price = self.entry_price * (1 + self.be_trigger)
                self.sl_price = self.entry_price * (1 + CONFIG.be_buffer)
                events['events'].append('break_even_activated')
            elif self.direction == 'Short' and current_price <= self.entry_price * (1 - self.be_trigger):
                self.be_activated = True
                self.be_price = self.entry_price * (1 - self.be_trigger)
                self.sl_price = self.entry_price * (1 - CONFIG.be_buffer)
                events['events'].append('break_even_activated')

        # Trailing Stop
        if not self.trailing_active:
            activation_price = self.entry_price * (1 + self.trailing_data['activation']) if self.direction == 'Long' else self.entry_price * (1 - self.trailing_data['activation'])
            if (self.direction == 'Long' and current_price >= activation_price) or \
               (self.direction == 'Short' and current_price <= activation_price):
                self.trailing_active = True
                self.trailing_sl = current_price * (1 - self.trailing_data['distance']) if self.direction == 'Long' else current_price * (1 + self.trailing_data['distance'])
                events['events'].append('trailing_activated')
        else:
            if self.direction == 'Long':
                new_sl = current_price * (1 - self.trailing_data['distance'])
                if new_sl > self.trailing_sl:
                    self.trailing_sl = new_sl
                    self.sl_price = new_sl
            else:
                new_sl = current_price * (1 + self.trailing_data['distance'])
                if new_sl < self.trailing_sl:
                    self.trailing_sl = new_sl
                    self.sl_price = new_sl

        # Timeout
        elapsed = (datetime.now() - self.entry_time).total_seconds() / 60
        if elapsed > CONFIG.max_hold_minutes:
            events['events'].append('timeout')

        return events

    def get_status(self) -> Dict:
        return {
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'sl_price': self.sl_price,
            'tp_price': self.tp_price,
            'size': self.size,
            'leverage': self.leverage,
            'be_activated': self.be_activated,
            'trailing_active': self.trailing_active,
            'trailing_sl': self.trailing_sl,
            'entry_time': self.entry_time,
            'be_trigger': self.be_trigger,
            'trailing_distance': self.trailing_data['distance']
        }