# config.py - VERSIÓN COMPLETA Y ESTABLE
import os

class CONFIG:
    """Configuración central del sistema JUNK TOYS Ω."""

    # ===== VERSIÓN =====
    version = '11.0.0'

    # ===== DIRECTORIOS =====
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(ROOT_DIR, 'cache')
    data_dir = os.path.join(ROOT_DIR, 'data')
    log_dir = os.path.join(ROOT_DIR, 'logs')

    # ===== UNIVERSO DE ACTIVOS (compatibles con OKX) =====
    universe = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT',
        'ADA/USDT', 'DOT/USDT', 'LINK/USDT', 'AVAX/USDT',
        'UNI/USDT', 'ATOM/USDT', 'NEAR/USDT', 'APT/USDT',
        'ARB/USDT', 'OP/USDT', 'INJ/USDT', 'SEI/USDT',
        'SUI/USDT', 'APE/USDT', 'FTM/USDT', 'ALGO/USDT',
        'ETC/USDT', 'LTC/USDT', 'DOGE/USDT'
    ]

    # ===== MODO FIRM SIGNALS (94% Win Rate) =====
    FIRM_MODE = True  # True para 94% Win Rate, False para modo clásico

    # ===== UMBRALES FIRM MODE =====
    FIRM_EDGE_THRESHOLD = 0.45
    FIRM_PIDELTA_THRESHOLD = 0.35
    FIRM_CONSENSUS_THRESHOLD = 0.50
    FIRM_REGIMES = ['Tendencia', 'Expansión']

    # ===== UMBRALES GENERALES =====
    EDGE_THRESHOLD = 0.10
    PIDELTA_THRESHOLD = 0.05
    CONFIDENCE_THRESHOLD = 0.40
    CONSENSUS_THRESHOLD = 0.25

    # ===== TIMEFRAMES =====
    TIMEFRAME = '5m'
    TIMEFRAMES_MTF = ['1m', '3m', '5m', '15m', '30m', '1h']

    # ===== BACKTEST =====
    BACKTEST_DAYS = 90

    # ===== RIESGO Y APALANCAMIENTO =====
    RISK_PER_TRADE = 0.018
    MAX_LEVERAGE = 10

    # ===== SL/TP OPTIMIZADOS (por defecto) =====
    SL_PCT_DEFAULT = 0.016
    TP_PCT_DEFAULT = 0.038

    # ===== BREAK EVEN (por defecto) =====
    BE_TRIGGER_DEFAULT = 0.0035
    BE_STATISTICAL_DEFAULT = 0.0025

    # ===== TRAILING STOP (por defecto) =====
    TRAILING_ACTIVATION_DEFAULT = 0.012
    TRAILING_DISTANCE_DEFAULT = 0.006

    # ===== PARÁMETROS POR ACTIVO (sobrescriben defaults) =====
    SL_PCT_BY_ASSET = {
        'BTC/USDT': 0.012, 'ETH/USDT': 0.015, 'BNB/USDT': 0.015,
        'SOL/USDT': 0.018, 'DOGE/USDT': 0.020,
    }

    TP_PCT_BY_ASSET = {
        'BTC/USDT': 0.030, 'ETH/USDT': 0.035, 'BNB/USDT': 0.035,
        'SOL/USDT': 0.040, 'DOGE/USDT': 0.045,
    }

    BE_TRIGGER_BY_ASSET = {
        'BTC/USDT': 0.0025, 'ETH/USDT': 0.0030, 'BNB/USDT': 0.0030,
        'SOL/USDT': 0.0035, 'DOGE/USDT': 0.0040,
    }

    TRAILING_ACTIVATION_BY_ASSET = {
        'BTC/USDT': 0.008, 'ETH/USDT': 0.010, 'BNB/USDT': 0.010,
        'SOL/USDT': 0.012, 'DOGE/USDT': 0.015,
    }

    TRAILING_DISTANCE_BY_ASSET = {
        'BTC/USDT': 0.004, 'ETH/USDT': 0.005, 'BNB/USDT': 0.005,
        'SOL/USDT': 0.006, 'DOGE/USDT': 0.008,
    }

    LEVERAGE_REC_BY_ASSET = {
        'BTC/USDT': 8, 'ETH/USDT': 7, 'BNB/USDT': 7,
        'SOL/USDT': 6, 'DOGE/USDT': 5,
    }
    LEVERAGE_REC_DEFAULT = 6

    LEVERAGE_MAX_BY_ASSET = {
        'BTC/USDT': 10, 'ETH/USDT': 9, 'BNB/USDT': 9,
        'SOL/USDT': 8, 'DOGE/USDT': 7,
    }
    LEVERAGE_MAX_DEFAULT = 8

    # ===== MÉTODOS AUXILIARES =====
    @classmethod
    def get_sl_pct(cls, symbol: str) -> float:
        return cls.SL_PCT_BY_ASSET.get(symbol, cls.SL_PCT_DEFAULT)

    @classmethod
    def get_tp_pct(cls, symbol: str) -> float:
        return cls.TP_PCT_BY_ASSET.get(symbol, cls.TP_PCT_DEFAULT)

    @classmethod
    def get_be_trigger(cls, symbol: str) -> float:
        return cls.BE_TRIGGER_BY_ASSET.get(symbol, cls.BE_TRIGGER_DEFAULT)

    @classmethod
    def get_trailing_activation(cls, symbol: str) -> float:
        return cls.TRAILING_ACTIVATION_BY_ASSET.get(symbol, cls.TRAILING_ACTIVATION_DEFAULT)

    @classmethod
    def get_trailing_distance(cls, symbol: str) -> float:
        return cls.TRAILING_DISTANCE_BY_ASSET.get(symbol, cls.TRAILING_DISTANCE_DEFAULT)

    @classmethod
    def get_leverage_rec(cls, symbol: str) -> float:
        return cls.LEVERAGE_REC_BY_ASSET.get(symbol, cls.LEVERAGE_REC_DEFAULT)

    @classmethod
    def get_leverage_max(cls, symbol: str) -> float:
        return cls.LEVERAGE_MAX_BY_ASSET.get(symbol, cls.LEVERAGE_MAX_DEFAULT)

    @classmethod
    def ensure_directories(cls):
        for d in [cls.cache_dir, cls.data_dir, cls.log_dir]:
            os.makedirs(d, exist_ok=True)

# Crear directorios automáticamente
CONFIG.ensure_directories()
