# config.py
"""
🧸 JUNK TOYS Ω — Configuración Central
Todos los parámetros ajustables del sistema se definen aquí.
"""

class CONFIG:
    # ============================================================
    # VERSIÓN
    # ============================================================
    version = '9.0.0'

    # ============================================================
    # ACTIVOS A MONITOREAR (UNIVERSO)
    # ============================================================
    universe = [
        'BTC/USDT',
        'ETH/USDT',
        'SOL/USDT',
        'BNB/USDT',
        'XRP/USDT'
    ]

    # ============================================================
    # GESTIÓN DE RIESGO
    # ============================================================
    risk_per_trade = 0.02      # 2% del capital por trade
    sl_pct = 0.02              # Stop Loss fijo (2%)
    tp_pct = 0.04              # Take Profit fijo (4%)
    max_leverage = 5           # Apalancamiento máximo permitido

    # ============================================================
    # BREAK EVEN
    # ============================================================
    be_trigger = 0.01          # Trigger para mover SL a BE (1% de beneficio)

    # ============================================================
    # BACKTEST
    # ============================================================
    backtest_days = 90         # Días de histórico para backtest automático

    # ============================================================
    # UMBRALES DE SEÑALES
    # ============================================================
    edge_threshold_high = 0.30   # Edge alto → señal fuerte
    edge_threshold_low = 0.10    # Edge mínimo → considerar señal
    confidence_threshold = 0.40  # Confianza mínima para aprobar señal

    # ============================================================
    # TIMEFRAMES (Multi-TimeFrame)
    # ============================================================
    timeframes = ['5m', '15m', '1h', '4h']

    # ============================================================
    # INDICADORES
    # ============================================================
    indicator_window = 100     # Velas necesarias para indicadores

    # ============================================================
    # MODO DEBUG
    # ============================================================
    debug = False              # Activar logs detallados
