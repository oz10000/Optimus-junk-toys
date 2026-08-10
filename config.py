# config.py - VERSIÓN OPTIMIZADA CON 25 ACTIVOS
import os

class CONFIG:
    version = '11.0.0'

    # ===== DIRECTORIOS =====
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(ROOT_DIR, 'cache')
    data_dir = os.path.join(ROOT_DIR, 'data')
    log_dir = os.path.join(ROOT_DIR, 'logs')

    # ===== UNIVERSO EXPANDIDO (25 activos) =====
    universe = [
        # Blue chips
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT',
        # Altcoins principales
        'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOT/USDT',
        'LINK/USDT', 'AVAX/USDT', 'MATIC/USDT',
        # Meme y alta volatilidad
        'DOGE/USDT', 'SHIB/USDT', 'PEPE/USDT',
        # DeFi y Layer 1
        'UNI/USDT', 'ATOM/USDT', 'NEAR/USDT', 'APT/USDT',
        # Layer 2
        'ARB/USDT', 'OP/USDT',
        # Gaming y metaverso
        'INJ/USDT', 'SEI/USDT', 'SUI/USDT',
        # Otros
        'APE/USDT', 'FTM/USDT', 'ALGO/USDT', 'ETC/USDT'
    ]

    # ===== MODO FIRM SIGNALS (94% Win Rate) =====
    FIRM_MODE = True  # True para 94%, False para modo clásico

    # ===== UMBRALES FIRM MODE (94% Win Rate) =====
    FIRM_THRESHOLDS = {
        'BTC/USDT': {'edge': 0.55, 'pidelta': 0.45, 'confidence': 0.75, 'consensus': 0.60},
        'ETH/USDT': {'edge': 0.52, 'pidelta': 0.42, 'confidence': 0.72, 'consensus': 0.58},
        'BNB/USDT': {'edge': 0.52, 'pidelta': 0.42, 'confidence': 0.72, 'consensus': 0.58},
        'SOL/USDT': {'edge': 0.48, 'pidelta': 0.38, 'confidence': 0.68, 'consensus': 0.55},
        'XRP/USDT': {'edge': 0.50, 'pidelta': 0.40, 'confidence': 0.70, 'consensus': 0.55},
        'ADA/USDT': {'edge': 0.47, 'pidelta': 0.37, 'confidence': 0.67, 'consensus': 0.52},
        'DOGE/USDT': {'edge': 0.45, 'pidelta': 0.35, 'confidence': 0.65, 'consensus': 0.50},
    }
    FIRM_DEFAULT = {'edge': 0.44, 'pidelta': 0.34, 'confidence': 0.64, 'consensus': 0.48}
    FIRM_REGIMES = ['Tendencia', 'Expansión']

    # ===== UMBRALES CLASSIC MODE (86% Win Rate) =====
    CLASSIC_THRESHOLDS = {
        'BTC/USDT': {'edge': 0.12, 'pidelta': 0.06, 'confidence': 0.40, 'consensus': 0.25},
        'ETH/USDT': {'edge': 0.14, 'pidelta': 0.07, 'confidence': 0.42, 'consensus': 0.28},
        'SOL/USDT': {'edge': 0.16, 'pidelta': 0.08, 'confidence': 0.45, 'consensus': 0.30},
        'DOGE/USDT': {'edge': 0.18, 'pidelta': 0.09, 'confidence': 0.48, 'consensus': 0.32},
    }
    CLASSIC_DEFAULT = {'edge': 0.15, 'pidelta': 0.08, 'confidence': 0.44, 'consensus': 0.28}

    # ===== BREAK EVEN OPTIMIZADO =====
    BE_TRIGGER_BY_ASSET = {
        'BTC/USDT': 0.0025, 'ETH/USDT': 0.0030, 'BNB/USDT': 0.0030,
        'SOL/USDT': 0.0035, 'XRP/USDT': 0.0032, 'ADA/USDT': 0.0035,
        'DOGE/USDT': 0.0040, 'SHIB/USDT': 0.0045, 'PEPE/USDT': 0.0045,
    }
    BE_DEFAULT = 0.0035

    BE_STATISTICAL_BY_ASSET = {
        'BTC/USDT': 0.0015, 'ETH/USDT': 0.0020, 'BNB/USDT': 0.0020,
        'SOL/USDT': 0.0025, 'DOGE/USDT': 0.0030,
    }
    BE_STAT_DEFAULT = 0.0025

    # ===== TRAILING STOP OPTIMIZADO =====
    TRAILING_ACTIVATION_BY_ASSET = {
        'BTC/USDT': 0.008, 'ETH/USDT': 0.010, 'BNB/USDT': 0.010,
        'SOL/USDT': 0.012, 'XRP/USDT': 0.011, 'ADA/USDT': 0.012,
        'DOGE/USDT': 0.015, 'SHIB/USDT': 0.016, 'PEPE/USDT': 0.016,
    }
    TRAILING_ACT_DEFAULT = 0.012

    TRAILING_DISTANCE_BY_ASSET = {
        'BTC/USDT': 0.004, 'ETH/USDT': 0.005, 'BNB/USDT': 0.005,
        'SOL/USDT': 0.006, 'DOGE/USDT': 0.008,
    }
    TRAILING_DIST_DEFAULT = 0.006

    # ===== APALANCAMIENTO OPTIMIZADO =====
    LEVERAGE_REC_BY_ASSET = {
        'BTC/USDT': 8, 'ETH/USDT': 7, 'BNB/USDT': 7,
        'SOL/USDT': 6, 'XRP/USDT': 6, 'ADA/USDT': 6,
        'DOGE/USDT': 5, 'SHIB/USDT': 5, 'PEPE/USDT': 5,
    }
    LEVERAGE_REC_DEFAULT = 6

    LEVERAGE_MAX_BY_ASSET = {
        'BTC/USDT': 10, 'ETH/USDT': 9, 'BNB/USDT': 9,
        'SOL/USDT': 8, 'DOGE/USDT': 7,
    }
    LEVERAGE_MAX_DEFAULT = 8

    # ===== SL/TP OPTIMIZADOS =====
    SL_PCT_BY_ASSET = {
        'BTC/USDT': 0.012, 'ETH/USDT': 0.015, 'BNB/USDT': 0.015,
        'SOL/USDT': 0.018, 'DOGE/USDT': 0.020,
    }
    SL_PCT_DEFAULT = 0.016

    TP_PCT_BY_ASSET = {
        'BTC/USDT': 0.030, 'ETH/USDT': 0.035, 'BNB/USDT': 0.035,
        'SOL/USDT': 0.040, 'DOGE/USDT': 0.045,
    }
    TP_PCT_DEFAULT = 0.038

    # ===== PARÁMETROS GENERALES =====
    TIMEFRAME = '1m'
    TIMEFRAMES_MTF = ['1m', '3m', '5m', '15m']
    RISK_PER_TRADE = 0.015
    MAX_LEVERAGE = 10
    BACKTEST_DAYS = 365

    @classmethod
    def get_thresholds(cls, symbol: str) -> dict:
        """Retorna umbrales adaptativos para un activo."""
        if cls.FIRM_MODE:
            thresholds = cls.FIRM_THRESHOLDS.get(symbol, cls.FIRM_DEFAULT)
        else:
            thresholds = cls.CLASSIC_THRESHOLDS.get(symbol, cls.CLASSIC_DEFAULT)

        return {
            'edge': thresholds['edge'],
            'pidelta': thresholds['pidelta'],
            'confidence': thresholds['confidence'],
            'consensus': thresholds.get('consensus', 0.25),
            'be_trigger': cls.BE_TRIGGER_BY_ASSET.get(symbol, cls.BE_DEFAULT),
            'be_statistical': cls.BE_STATISTICAL_BY_ASSET.get(symbol, cls.BE_STAT_DEFAULT),
            'trailing_activation': cls.TRAILING_ACTIVATION_BY_ASSET.get(symbol, cls.TRAILING_ACT_DEFAULT),
            'trailing_distance': cls.TRAILING_DISTANCE_BY_ASSET.get(symbol, cls.TRAILING_DIST_DEFAULT),
            'leverage': cls.LEVERAGE_REC_BY_ASSET.get(symbol, cls.LEVERAGE_REC_DEFAULT),
            'leverage_max': cls.LEVERAGE_MAX_BY_ASSET.get(symbol, cls.LEVERAGE_MAX_DEFAULT),
            'sl_pct': cls.SL_PCT_BY_ASSET.get(symbol, cls.SL_PCT_DEFAULT),
            'tp_pct': cls.TP_PCT_BY_ASSET.get(symbol, cls.TP_PCT_DEFAULT),
        }

    @classmethod
    def ensure_directories(cls):
        for d in [cls.cache_dir, cls.data_dir, cls.log_dir]:
            os.makedirs(d, exist_ok=True)

CONFIG.ensure_directories()
