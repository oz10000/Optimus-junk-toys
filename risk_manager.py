# risk_manager.py
from config import CONFIG

class RiskManager:
    def __init__(self, streak_engine=None):
        self.streak = streak_engine
        self.daily_pnl = 0.0
        self.daily_trades = 0

    def get_position_size(self, capital: float, leverage: int, 
                          entry_price: float, risk_pct: float = None) -> float:
        risk = risk_pct or CONFIG.risk_per_trade
        if self.streak is not None:
            multiplier = self.streak.get_position_size_multiplier()
        else:
            multiplier = 1.0
        adjusted_risk = risk * multiplier
        position_value = capital * leverage * adjusted_risk
        return position_value / entry_price if entry_price > 0 else 0
