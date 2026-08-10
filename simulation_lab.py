# simulation_lab.py
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

class SimulationLab:
    """
    Laboratorio de simulación continua.
    Ejecuta escaneos automáticos cada 5 minutos sobre datos históricos.
    """
    
    def __init__(self, data_provider, decision_engine, history: List[Dict]):
        self.data = data_provider
        self.engine = decision_engine
        self.history = history
        self.results = []
        self.scan_log = []
    
    def run_historical_scan(self, symbol: str, start_date: datetime, 
                           end_date: datetime, timeframe: str = '5m') -> Dict:
        """
        Ejecuta un escaneo histórico simulando escaneos cada 5 minutos.
        
        Args:
            symbol: Activo a escanear
            start_date: Fecha de inicio
            end_date: Fecha de fin
            timeframe: Timeframe base
        
        Returns:
            Dict con resultados del escaneo
        """
        # Obtener datos históricos completos
        df = self.data.get_ohlcv(symbol, timeframe=timeframe, limit=10000)
        if df is None or df.empty:
            return {'error': 'No data available'}
        
        # Filtrar por rango de fechas
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        if df.empty:
            return {'error': 'No data in date range'}
        
        # Simular escaneos cada 5 minutos
        signals = []
        scan_times = []
        scan_interval = 5  # minutos
        
        current_time = start_date
        while current_time <= end_date:
            # Obtener datos hasta current_time
            data_up_to = df[df.index <= current_time]
            if len(data_up_to) >= 100:
                # Ejecutar decisión
                decision = self.engine.evaluate(symbol, data_up_to)
                if decision:
                    signals.append({
                        'timestamp': current_time,
                        'decision': decision,
                        'symbol': symbol
                    })
                    scan_times.append(current_time)
            
            current_time += timedelta(minutes=scan_interval)
        
        # Estadísticas del escaneo
        total_scans = len(scan_times)
        signals_found = len(signals)
        
        # Calcular intervalos entre señales
        intervals = []
        for i in range(1, len(signals)):
            delta = (signals[i]['timestamp'] - signals[i-1]['timestamp']).total_seconds() / 60
            intervals.append(delta)
        
        avg_interval = np.mean(intervals) if intervals else 0
        std_interval = np.std(intervals) if intervals else 0
        
        return {
            'symbol': symbol,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_scans': total_scans,
            'signals_found': signals_found,
            'signal_density': signals_found / total_scans if total_scans > 0 else 0,
            'avg_interval_minutes': avg_interval,
            'std_interval_minutes': std_interval,
            'first_signal': signals[0]['timestamp'].isoformat() if signals else None,
            'last_signal': signals[-1]['timestamp'].isoformat() if signals else None,
            'signals': signals
        }
    
    def run_continuous_simulation(self, symbols: List[str], 
                                  days: int = 30) -> Dict:
        """
        Ejecuta simulación continua para múltiples activos.
        
        Args:
            symbols: Lista de activos
            days: Número de días a simular
        
        Returns:
            Dict con resultados agregados
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        results = {}
        for symbol in symbols:
            print(f"Simulando {symbol}...")
            result = self.run_historical_scan(symbol, start_date, end_date)
            results[symbol] = result
        
        # Agregar estadísticas globales
        all_intervals = []
        all_densities = []
        
        for symbol, result in results.items():
            if 'avg_interval_minutes' in result and result['avg_interval_minutes'] > 0:
                all_intervals.append(result['avg_interval_minutes'])
            if 'signal_density' in result:
                all_densities.append(result['signal_density'])
        
        return {
            'results': results,
            'global_stats': {
                'avg_interval_all': np.mean(all_intervals) if all_intervals else 0,
                'std_interval_all': np.std(all_intervals) if all_intervals else 0,
                'avg_density_all': np.mean(all_densities) if all_densities else 0,
                'total_signals': sum(r.get('signals_found', 0) for r in results.values()),
                'total_scans': sum(r.get('total_scans', 0) for r in results.values())
            }
        }
