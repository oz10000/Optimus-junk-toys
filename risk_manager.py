# risk_manager.py
from config import CONFIG

class RiskManager:
    """Gestiona el riesgo por trade y ajusta según rachas."""

    def __init__(self, streak_engine=None):
        self.streak = streak_engine
        self.daily_pnl = 0.0
        self.daily_trades = 0

    def get_position_size(self, capital: float, leverage: int, entry_price: float,
                          risk_pct: float = None) -> float:
        """Calcula el tamaño de posición en unidades del activo."""
        risk = risk_pct or CONFIG.risk_per_trade
        # Ajuste por rachas
        if self.streak:
            multiplier = self.streak.get_position_size_multiplier()
        else:
            multiplier = 1.0
        adjusted_risk = risk * multiplier
        position_value = capital * leverage * adjusted_risk
        return position_value / entry_price

    def update_daily(self, pnl: float):
        self.daily_pnl += pnl
        self.daily_trades += 1

    def reset_daily(self):
        self.daily_pnl = 0.0
        self.daily_trades = 0

    def can_trade(self) -> bool:
        """Verifica si se puede operar según límite diario."""
        if self.daily_trades >= CONFIG.max_positions:
            return False
        if self.daily_pnl < -CONFIG.max_daily_loss * CONFIG.initial_capital:
            return False
        return True
