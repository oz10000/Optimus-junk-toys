# streamlit_app.py
import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from config import CONFIG
from data import DataProvider
from decision_engine import DecisionEngine
from signal_generator import SignalGenerator
from ranking import Ranking
from storage import Storage
from backtest import Backtest
from walk_forward import WalkForward
from monte_carlo import MonteCarlo
from metrics import Metrics
from performance import Performance
from streak_analyzer import StreakAnalyzer
from distribution_analyzer import DistributionAnalyzer
from temporal_confidence import TemporalConfidence
from shun_toy_level import ShunToyLevel
from top_opportunities import TopOpportunities
from timing_engine import TimingEngine

st.set_page_config(
    page_title="🧸 JUNK TOYS Ω",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# INICIALIZACIÓN CON BACKTEST AUTOMÁTICO
# ============================================================
if 'initialized' not in st.session_state:
    st.session_state.data = DataProvider()
    st.session_state.storage = Storage()
    st.session_state.history = []
    st.session_state.signals = []
    st.session_state.last_scan = None
    st.session_state.backtest_done = False
    st.session_state.initialized = True

# Verificar si el historial existe y es suficiente
def ensure_history():
    """Asegura que el historial tenga al menos 2 trades, ejecutando backtest si es necesario."""
    history = st.session_state.history
    if len(history) >= 2:
        return

    # Intentar cargar desde almacenamiento persistente
    stored = st.session_state.storage.load('history')
    if stored and len(stored) >= 2:
        st.session_state.history = stored
        return

    # Si no hay historial persistente, ejecutar backtest automático
    with st.spinner("🔄 Reconstruyendo historial mediante backtest automático..."):
        # Obtener símbolos del universo
        symbols = CONFIG.universe
        if not symbols:
            symbols = ['BTC/USDT', 'ETH/USDT']

        # Definir período histórico (últimos 90 días)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        # Instanciar motores
        data_provider = st.session_state.data
        engine = DecisionEngine(data_provider, None, [])  # historial vacío al inicio
        backtest = Backtest(data_provider, engine)

        # Ejecutar backtest
        result = backtest.run(symbols, start_date, end_date, timeframe='5m')
        trades = result.get('trades', [])

        if len(trades) >= 2:
            st.session_state.history = trades
            # Guardar en almacenamiento
            st.session_state.storage.save('history', trades)
            st.success(f"✅ Historial reconstruido con {len(trades)} trades.")
        else:
            st.warning("⚠️ No se pudieron generar suficientes trades con los datos disponibles. Verifica la conexión y los símbolos.")
            # Opcional: crear un historial mínimo con datos de ejemplo (pero no simulados)
            # En este caso, preferimos mostrar un mensaje de error y no inventar datos.
            # Se puede intentar con un período más largo.
            # Si aún así falla, se deja el historial vacío.

# Ejecutar la verificación al inicio
ensure_history()

# ============================================================
# SIDEBAR Y DEMÁS (igual que antes, pero usando history real)
# ============================================================
# ... (el resto del sidebar y pestañas se mantiene igual, pero ahora history ya tiene datos reales)
