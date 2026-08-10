# indicators.py - VERSIÓN CORREGIDA CON MÉTODO compute
import numpy as np
import pandas as pd
from typing import Optional, Dict


class Indicators:
    """Cálculo de indicadores técnicos para JUNK TOYS Ω."""

    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> float:
        """Average Directional Index."""
        high, low, close = df['high'], df['low'], df['close']
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift())))
        atr = tr.rolling(period).mean()
        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        plus_di = 100 * pd.Series(plus_dm).rolling(period).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(period).mean() / atr
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
        adx = dx.rolling(period).mean()
        return adx.iloc[-1] if len(adx) > 0 else 25.0

    @staticmethod
    def ker(df: pd.DataFrame, period: int = 10) -> float:
        """Kaufman Efficiency Ratio."""
        close = df['close']
        change = abs(close.diff(period))
        volatility = abs(close.diff()).rolling(period).sum()
        ker = change / (volatility + 1e-9)
        return ker.iloc[-1] if len(ker) > 0 else 0.3

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> float:
        """Average True Range."""
        high, low, close = df['high'], df['low'], df['close']
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift())))
        atr = tr.rolling(period).mean()
        return atr.iloc[-1] if len(atr) > period else 0.0

    @staticmethod
    def pidelta(df: pd.DataFrame) -> float:
        """PiDelta Score basado en MACD histograma normalizado."""
        close = df['close']
        ema9 = close.ewm(span=9).mean()
        ema21 = close.ewm(span=21).mean()
        macd = ema9 - ema21
        signal = macd.ewm(span=9).mean()
        hist = macd - signal
        norm_hist = hist / (hist.std() + 1e-9)
        pidelta = norm_hist.iloc[-1] if len(norm_hist) > 0 else 0.0
        return np.clip(pidelta, -1, 1)

    @staticmethod
    def compute(df: pd.DataFrame) -> Optional[Dict]:
        """
        Calcula todos los indicadores y los devuelve en un diccionario.
        Este es el método que usa DecisionEngine.
        """
        if df is None or len(df) < 50:
            return None

        return {
            'adx': Indicators.adx(df),
            'atr': Indicators.atr(df),
            'ker': Indicators.ker(df),
            'pidelta': Indicators.pidelta(df),
        }
