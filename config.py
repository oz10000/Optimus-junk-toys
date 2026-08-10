# config.py
"""
Configuración centralizada del sistema JUNK TOYS Ω.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os

@dataclass
class Config:
    # ==================== DATOS ====================
    timeframe: str = '5m'
    timeframes: List[str] = field(default_factory=lambda: ['1m','3m','5m','15m','30m','1h','2h','4h','8h','1D'])
    lookback_days: int = 365
    initial_capital: float = 10000.0
    commission: float = 0.0004
    slippage: float = 0.0005

    # ==================== ACTIVOS ====================
    universe: List[str] = field(default_factory=lambda: [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'LTC/USDT',
        'BNB/USDT', 'ADA/USDT'
    ])

    # ==================== UMBRALES ====================
    min_score: float = 0.35
    adx_threshold: float = 25.0
    ker_threshold: float = 0.48

    # ==================== TP/SL ====================
    tp_mult: float = 2.2
    sl_mult: float = 0.9

    # ==================== TRAILING STOP ====================
    trailing_distance: float = 0.010
    trailing_activation: float = 0.015
    trailing_callback: float = 0.003

    # ==================== BREAK EVEN ====================
    be_trigger: float = 0.004
    be_buffer: float = 0.0015

    # ==================== TIEMPO ====================
    max_hold_minutes: int = 90
    cooldown_minutes: int = 30

    # ==================== RIESGO ====================
    max_leverage: int = 12
    risk_per_trade: float = 0.015
    max_positions: int = 3
    max_daily_loss: float = 0.08

    # ==================== RACHAS ====================
    block_size: int = 2
    ww_bonus: float = 1.10
    ll_penalty: float = 0.80
    max_consecutive_losses: int = 3

    # ==================== HORARIO ====================
    hour_filter_start: int = 10
    hour_filter_end: int = 17
    optimal_hours: List[tuple] = field(default_factory=lambda: [(10, 12)])
    hour_multiplier: float = 1.2

    # ==================== PESOS PIDELTA ====================
    pidelta_weights: Dict[str, float] = field(default_factory=lambda: {
        'trend': 0.22, 'strength': 0.22, 'ker': 0.18,
        'atr_rel': 0.10, 'momentum': 0.08
    })

    # ==================== PESOS MULTI-TIMEFRAME ====================
    mtf_weights: Dict[str, float] = field(default_factory=lambda: {
        '1m': 0.02, '3m': 0.08, '5m': 0.28, '15m': 0.24,
        '30m': 0.18, '1h': 0.12, '2h': 0.04, '4h': 0.03, '8h': 0.01
    })

    # ==================== DIRECTORIOS ====================
    data_dir: str = 'data'
    cache_dir: str = 'data/cache'
    results_dir: str = 'data/results'
    logs_dir: str = 'logs'

    # ==================== VERSIÓN ====================
    version: str = '9.0.0'

    def __post_init__(self):
        for d in [self.data_dir, self.cache_dir, self.results_dir, self.logs_dir]:
            os.makedirs(d, exist_ok=True)

CONFIG = Config()
