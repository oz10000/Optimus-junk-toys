# config.py
import os

class CONFIG:
    """
    Configuración central del sistema JUNK TOYS Ω.
    Todos los parámetros ajustables se definen aquí.
    """

    # ===== VERSIÓN =====
    version = '9.0.0'

    # ===== DIRECTORIOS =====
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(ROOT_DIR, 'cache')
    data_dir = os.path.join(ROOT_DIR, 'data')
    log_dir = os.path.join(ROOT_DIR, 'logs')

    # ===== ACTIVOS (UNIVERSO) =====
    # Símbolos compatibles con OKX, Binance, KuCoin, etc.
    universe = [
        'BTC/USDT',
        'ETH/USDT',
        'SOL/USDT',
        'XRP/USDT',
        'ADA/USDT',
        'DOT/USDT',
        'LINK/USDT',
        'AVAX/USDT',
        'MATIC/USDT',
        'UNI/USDT',
    ]

    # ===== GESTIÓN DE RIESGO =====
    risk_per_trade = 0.02      # 2% del capital por trade
    sl_pct = 0.02              # Stop Loss fijo (2%)
    tp_pct = 0.04              # Take Profit fijo (4%)
    max_leverage = 5           # Apalancamiento máximo permitido

    # ===== BREAK EVEN =====
    be_trigger = 0.01          # Trigger para mover SL a BE (1% de beneficio)

    # ===== BACKTEST =====
    backtest_days = 90         # Días de histórico para backtest automático

    # ===== UMBRALES DE SEÑALES =====
    edge_threshold_high = 0.30   # Edge alto → señal fuerte
    edge_threshold_low = 0.10    # Edge mínimo → considerar señal
    confidence_threshold = 0.40  # Confianza mínima para aprobar señal

    # ===== TIMEFRAMES (Multi‑TimeFrame) =====
    timeframes = ['5m', '15m', '1h', '4h']

    # ===== INDICADORES =====
    indicator_window = 100     # Velas necesarias para indicadores

    # ===== MODO DEBUG =====
    debug = False              # Activar logs detallados

    @classmethod
    def ensure_directories(cls):
        """Crea los directorios necesarios si no existen."""
        for dir_path in [cls.cache_dir, cls.data_dir, cls.log_dir]:
            os.makedirs(dir_path, exist_ok=True)

# Crear directorios automáticamente al importar
CONFIG.ensure_directories()
