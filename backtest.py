# backtest.py
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from data import DataProvider
from decision_engine import DecisionEngine
from trailing_engine import TrailingEngine
from break_even_engine import BreakEvenEngine

class Backtest:
    """
    Ejecuta un backtest histórico utilizando el Decision Engine real.
    Genera un historial detallado de trades con todos los campos necesarios.
    """

    def __init__(self, data_provider: DataProvider, decision_engine: DecisionEngine):
        self.data = data_provider
        self.engine = decision_engine
        self.trades = []

    def run(self, symbols: List[str], start_date: datetime, end_date: datetime,
            timeframe: str = '5m', initial_capital: float = 10000.0) -> Dict:
        """
        Ejecuta backtest sobre el período indicado.

        Retorna:
            Dict con:
                - trades: Lista de diccionarios con todos los campos
                - metrics: métricas calculadas desde los trades
                - n_trades: int
        """
        self.trades = []
        capital = initial_capital

        for symbol in symbols:
            df = self.data.get_ohlcv(symbol, timeframe=timeframe, limit=10000)
            if df is None or df.empty:
                continue
            # Filtrar por fechas
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            if df.empty:
                continue

            # Variables de estado para simulación
            position = None  # {'entry_price', 'direction', 'entry_time', 'stop_loss', 'take_profit', 'trailing_stop'}
            # Recorrer cada vela
            for i in range(100, len(df)):
                current_time = df.index[i]
                current_price = df.iloc[i]['close']
                # Obtener datos hasta el momento actual para el decision engine
                data_slice = df.iloc[:i+1]
                if len(data_slice) < 100:
                    continue

                # Si no hay posición, evaluar señal
                if position is None:
                    decision = self.engine.evaluate(symbol, data_slice)
                    if decision and decision.get('action') in ['BUY', 'SELL']:
                        # Crear posición
                        direction = 'LONG' if decision['action'] == 'BUY' else 'SHORT'
                        entry_price = current_price
                        # Obtener SL y TP desde la decisión (o usar valores por defecto)
                        sl_pct = decision.get('sl_pct', 0.02)  # 2%
                        tp_pct = decision.get('tp_pct', 0.04)  # 4%
                        stop_loss = entry_price * (1 - sl_pct) if direction == 'LONG' else entry_price * (1 + sl_pct)
                        take_profit = entry_price * (1 + tp_pct) if direction == 'LONG' else entry_price * (1 - tp_pct)
                        # Calcular trailing stop y break even
                        atr = decision.get('atr', 0)
                        adx = decision.get('adx', 25)
                        volatility = decision.get('volatility', 0.01)
                        regime = decision.get('regime', 'Normal')
                        trailing_info = TrailingEngine.compute(entry_price, atr, adx, volatility, regime, 0.01)
                        be_info = BreakEvenEngine.select_best(entry_price, atr, volatility)

                        position = {
                            'symbol': symbol,
                            'direction': direction,
                            'entry_price': entry_price,
                            'entry_time': current_time,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'trailing_stop': trailing_info['distance'],
                            'trailing_activation': trailing_info['activation'],
                            'be_trigger': be_info['trigger'],
                            'sl_pct': sl_pct,
                            'tp_pct': tp_pct,
                            'regime': regime,
                            'volatility': volatility,
                            'atr': atr,
                            'adx': adx,
                            'highest_price': entry_price,
                            'lowest_price': entry_price,
                            'trailing_active': False,
                            'be_applied': False,
                            'reason_exit': None
                        }
                        # Reducir capital por riesgo (simplificado)
                        # (En una implementación real, se usaría risk_manager)
                else:
                    # Actualizar trailing stop y break even
                    if position['direction'] == 'LONG':
                        # Actualizar máximo
                        if current_price > position['highest_price']:
                            position['highest_price'] = current_price
                            # Activar trailing si se supera la activación
                            if not position['trailing_active'] and current_price > position['entry_price'] * (1 + position['trailing_activation']):
                                position['trailing_active'] = True
                            # Si trailing activo, subir stop_loss
                            if position['trailing_active']:
                                new_stop = current_price * (1 - position['trailing_stop'])
                                if new_stop > position['stop_loss']:
                                    position['stop_loss'] = new_stop
                            # Aplicar break even si se supera el trigger
                            if not position['be_applied'] and current_price > position['entry_price'] * (1 + position['be_trigger']):
                                position['stop_loss'] = position['entry_price']  # llevar a BE
                                position['be_applied'] = True
                    else:  # SHORT
                        if current_price < position['lowest_price']:
                            position['lowest_price'] = current_price
                            if not position['trailing_active'] and current_price < position['entry_price'] * (1 - position['trailing_activation']):
                                position['trailing_active'] = True
                            if position['trailing_active']:
                                new_stop = current_price * (1 + position['trailing_stop'])
                                if new_stop < position['stop_loss']:
                                    position['stop_loss'] = new_stop
                            if not position['be_applied'] and current_price < position['entry_price'] * (1 - position['be_trigger']):
                                position['stop_loss'] = position['entry_price']
                                position['be_applied'] = True

                    # Verificar condiciones de salida
                    exit_reason = None
                    exit_price = None
                    if position['direction'] == 'LONG':
                        if current_price <= position['stop_loss']:
                            exit_price = position['stop_loss']
                            exit_reason = 'Stop Loss'
                        elif current_price >= position['take_profit']:
                            exit_price = position['take_profit']
                            exit_reason = 'Take Profit'
                    else:  # SHORT
                        if current_price >= position['stop_loss']:
                            exit_price = position['stop_loss']
                            exit_reason = 'Stop Loss'
                        elif current_price <= position['take_profit']:
                            exit_price = position['take_profit']
                            exit_reason = 'Take Profit'

                    if exit_price is not None:
                        # Cerrar posición
                        pnl_pct = (exit_price - position['entry_price']) / position['entry_price']
                        if position['direction'] == 'SHORT':
                            pnl_pct = -pnl_pct
                        duration_minutes = (current_time - position['entry_time']).total_seconds() / 60

                        # Registrar trade
                        trade = {
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
                            'sl_pct': position['sl_pct'],
                            'tp_pct': position['tp_pct']
                        }
                        self.trades.append(trade)
                        # Actualizar capital (simplificado: se reinvierte todo)
                        capital *= (1 + pnl_pct)
                        # Resetear posición
                        position = None

        # Calcular métricas sobre los trades generados
        from metrics import Metrics
        metrics = Metrics.compute(self.trades) if self.trades else {}

        return {
            'trades': self.trades,
            'metrics': metrics,
            'n_trades': len(self.trades),
            'final_capital': capital
        }
