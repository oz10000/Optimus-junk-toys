# config.py
import os

class CONFIG:
    # ===== VERSIÓN =====
    version = '9.0.0'

    # ===== DIRECTORIOS =====
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(ROOT_DIR, 'cache')
    data_dir = os.path.join(ROOT_DIR, 'data')
    log_dir = os.path.join(ROOT_DIR, 'logs')

    # ===== ACTIVOS (se certificarán automáticamente) =====
    universe = [
        'BTC/USDT',
        'ETH/USDT',
        'SOL/USDT',
        'BNB/USDT',
        'XRP/USDT',
        'ADA/USDT',
        'DOT/USDT',
        'LINK/USDT',
        'AVAX/USDT',
        'MATIC/USDT',
    ]

    # ===== GESTIÓN DE RIESGO =====
    risk_per_trade = 0.02
    sl_pct = 0.02
    tp_pct = 0.04
    max_leverage = 5

    # ===== BREAK EVEN =====
    be_trigger = 0.01

    # ===== BACKTEST =====
    backtest_days = 90

    # ===== UMBRALES =====
    edge_threshold_high = 0.30
    edge_threshold_low = 0.10
    confidence_threshold = 0.40

    # ===== TIMEFRAMES =====
    timeframes = ['5m', '15m', '1h', '4h']

    # ===== INDICADORES =====
    indicator_window = 100

    # ===== DEBUG =====
    debug = False

    @classmethod
    def ensure_directories(cls):
        for dir_path in [cls.cache_dir, cls.data_dir, cls.log_dir]:
            os.makedirs(dir_path, exist_ok=True)

# Crear directorios
CONFIG.ensure_directories()
