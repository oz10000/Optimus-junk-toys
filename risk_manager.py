# risk_manager.py (CORREGIDO)
from config import CONFIG

class RiskManager:
    """Gestiona el riesgo por trade y ajusta según rachas."""
    
    def __init__(self, streak_engine=None):
        self.streak = streak_engine
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def get_position_size(self, capital: float, leverage: int, 
                          entry_price: float, risk_pct: float = None) -> float:
        """Calcula el tamaño de posición en unidades del activo."""
        risk = risk_pct or CONFIG.risk_per_trade
        
        # Ajuste por rachas (solo si streak_engine no es None)
        if self.streak is not None:
            multiplier = self.streak.get_position_size_multiplier()
        else:
            multiplier = 1.0
        
        adjusted_risk = risk * multiplier
        position_value = capital * leverage * adjusted_risk
        return position_value / entry_price if entry_price > 0 else 0
    
    # ... resto del código sin cambios
