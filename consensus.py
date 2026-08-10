# consensus.py
import numpy as np
import pandas as pd

class Consensus:
    """
    Consenso multi-timeframe.
    Evalúa la tendencia en múltiples plazos y genera un score.
    """

    @staticmethod
    def compute(df: pd.DataFrame) -> float:
        """
        Retorna un score de consenso entre -1 y 1.
        """
        if df is None or len(df) < 100:
            return 0.0

        close = df['close']

        # Calcular pendientes en diferentes plazos (simulado)
        # Usamos ventanas de diferentes tamaños como aproximación a múltiples timeframes
        def slope(series, window):
            if len(series) < window:
                return 0.0
            x = np.arange(window)
            y = series.iloc[-window:].values
            if np.std(x) == 0:
                return 0.0
            return np.polyfit(x, y, 1)[0]

        slopes = {
            'short': slope(close, 12),   # ~1 hora en 5m
            'medium': slope(close, 24),  # ~2 horas
            'long': slope(close, 48),    # ~4 horas
        }

        # Normalizar pendientes a [-1, 1] usando volatilidad
        vol = close.pct_change().std()
        if vol == 0:
            vol = 0.01
        normalized = {k: np.clip(v / (vol * 100), -1, 1) for k, v in slopes.items()}

        # Ponderación: más peso a plazos más largos
        weights = {'short': 0.2, 'medium': 0.3, 'long': 0.5}
        consensus = sum(normalized[k] * weights[k] for k in weights)

        return np.clip(consensus, -1, 1)
