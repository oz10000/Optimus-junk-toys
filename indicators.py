# indicators.py
import pandas as pd
import numpy as np
from typing import Tuple, Optional

class Indicators:
    """Conjunto completo de indicadores técnicos."""

    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> float:
        """Average Directional Index (ADX)."""
        if df.empty or len(df) < period:
            return 0.0
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values

        plus_dm = np.zeros(len(high))
        minus_dm = np.zeros(len(high))
        for i in range(1, len(high)):
            up = high[i] - high[i-1]
            down = low[i-1] - low[i]
            if up > down and up > 0:
                plus_dm[i] = up
            if down > up and down > 0:
                minus_dm[i] = down

        tr = np.maximum(high - low,
                        np.maximum(abs(high - np.roll(close, 1)),
                                   abs(low - np.roll(close, 1))))
        tr[0] = 0

        atr = pd.Series(tr).rolling(period).mean().values
        plus_di = 100 * (pd.Series(plus_dm).rolling(period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
        adx = dx.rolling(period).mean()
        return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0.0

    @staticmethod
    def ker(df: pd.DataFrame, period: int = 10) -> float:
        """Kaufman Efficiency Ratio (KER)."""
        if df.empty or len(df) < period:
            return 0.0
        close = df['close']
        change = abs(close.diff(period))
        volatility = close.diff().abs().rolling(period).sum()
        ker = (change / (volatility + 1e-9)).fillna(0)
        return float(ker.iloc[-1]) if not pd.isna(ker.iloc[-1]) else 0.0

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> float:
        """Average True Range (ATR)."""
        if df.empty or len(df) < period:
            return 0.0
        high, low, close = df['high'], df['low'], df['close']
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        return float(tr.rolling(period).mean().iloc[-1]) if len(tr) > 0 else 0.0

    @staticmethod
    def ema(df: pd.DataFrame, period: int = 22) -> float:
        """Exponential Moving Average (último valor)."""
        if df.empty or len(df) < period:
            return df['close'].iloc[-1] if not df.empty else 0.0
        return float(df['close'].ewm(span=period, adjust=False).mean().iloc[-1])

    @staticmethod
    def vwap(df: pd.DataFrame) -> float:
        """Volume Weighted Average Price (último valor)."""
        if df.empty or df['volume'].sum() == 0:
            return df['close'].iloc[-1] if not df.empty else 0.0
        vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        return float(vwap.iloc[-1])

    @staticmethod
    def momentum(df: pd.DataFrame, period: int = 5) -> float:
        """Momentum normalizado por ATR."""
        if df.empty or len(df) < period:
            return 0.0
        mom = df['close'].pct_change(period).iloc[-1]
        atr_val = Indicators.atr(df, 14)
        if atr_val == 0:
            return 0.0
        return float(mom / (atr_val / df['close'].iloc[-1]))

    @staticmethod
    def volatility(df: pd.DataFrame, period: int = 20) -> float:
        """Volatilidad anualizada."""
        if df.empty or len(df) < period:
            return 0.0
        returns = df['close'].pct_change().dropna()
        if len(returns) < period:
            return 0.0
        return float(returns.iloc[-period:].std() * np.sqrt(252) * 100)

    @staticmethod
    def volume_ratio(df: pd.DataFrame, period: int = 20) -> float:
        """Volumen relativo a la media móvil."""
        if df.empty or len(df) < period:
            return 1.0
        vol = df['volume']
        avg = vol.rolling(period).mean().iloc[-1]
        return float(vol.iloc[-1] / avg) if avg > 0 else 1.0
