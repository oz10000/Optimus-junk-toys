# market_regime.py
from indicators import Indicators

class MarketRegime:
    """Clasifica el régimen de mercado actual."""

    @staticmethod
    def detect(df) -> str:
        if df.empty or len(df) < 30:
            return 'Normal'

        adx = Indicators.adx(df, 14)
        atr_val = Indicators.atr(df, 14)
        close = df['close'].iloc[-1]
        atr_pct = atr_val / close if close > 0 else 0

        if adx > 40 and atr_pct > 0.02:
            return 'Expansión'
        elif adx > 30:
            return 'Tendencia Fuerte'
        elif adx > 22:
            return 'Tendencia'
        elif adx < 15:
            return 'Chop'
        else:
            return 'Normal'