# pidelta.py
import numpy as np
from config import CONFIG
from indicators import Indicators

class PiDeltaScore:
    """PiDelta Score compuesto con pesos optimizados."""

    @staticmethod
    def compute(df) -> float:
        if df.empty or len(df) < 30:
            return 0.0

        close = df['close'].iloc[-1]
        atr_val = Indicators.atr(df, 14)
        if atr_val == 0:
            return 0.0

        ema = Indicators.ema(df, 22)
        adx = Indicators.adx(df, 14)
        ker = Indicators.ker(df, 10)

        w = CONFIG.pidelta_weights
        trend = np.tanh((close - ema) / atr_val)
        strength = min(1.0, adx / 40.0)
        ker_val = ker
        atr_rel = min(1.0, (atr_val / close) / 0.035)
        mom = Indicators.momentum(df, 5)
        mom_norm = np.tanh(mom * 5)

        raw = (w['trend'] * trend +
               w['strength'] * strength +
               w['ker'] * ker_val +
               w['atr_rel'] * atr_rel +
               w['momentum'] * mom_norm)

        return float(np.tanh(raw))