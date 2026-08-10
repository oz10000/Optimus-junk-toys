# break_even_engine.py
import numpy as np
from typing import Dict, List, Optional

class BreakEvenEngine:
    """Calcula el Break Even estadístico basado en ATR y volatilidad histórica."""
    
    @staticmethod
    def select_best(entry_price: float, atr: float, volatility: float, 
                    history: Optional[List[Dict]] = None) -> Dict:
        """
        Selecciona el mejor trigger de Break Even.
        
        Args:
            entry_price: Precio de entrada
            atr: Average True Range
            volatility: Volatilidad actual
            history: Historial de trades (opcional)
        
        Returns:
            Dict con trigger, confidence, y métricas
        """
        atr_pct = atr / entry_price if entry_price > 0 else 0.005
        
        # Trigger base: 0.75x ATR
        base_trigger = atr_pct * 0.75
        
        # Ajuste por volatilidad
        vol_factor = 0.5 + 0.5 * min(volatility / 0.02, 2.0)
        trigger = base_trigger * vol_factor
        
        # Limitar entre 0.2% y 3%
        trigger = max(0.002, min(0.03, trigger))
        
        # Si hay historial, ajustar con el win rate histórico
        confidence = 0.5
        if history and len(history) > 0:
            wins = sum(1 for t in history if t.get('pnl_pct', 0) > 0)
            win_rate = wins / len(history) if history else 0.5
            # Si el win rate es alto, podemos usar un trigger más agresivo
            if win_rate > 0.6:
                trigger *= 0.9
                confidence = 0.7
            elif win_rate < 0.4:
                trigger *= 1.1
                confidence = 0.3
        
        return {
            'trigger': trigger,
            'trigger_pct': trigger * 100,
            'confidence': confidence,
            'atr_pct': atr_pct,
            'volatility_factor': vol_factor,
            'method': 'statistical'
        }
