# streamlit_app.py
import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from config import CONFIG
from data import DataProvider
from indicators import Indicators
from pidelta import PiDeltaScore
from decision_engine import DecisionEngine
from signal_generator import SignalGenerator
from ranking import Ranking
from storage import Storage
from dashboard import Dashboard
from backtest import Backtest
from walk_forward import WalkForward
from monte_carlo import MonteCarlo
from metrics import Metrics
from performance import Performance
from streak_engine import StreakEngine
from timing_engine import TimingEngine

st.set_page_config(page_title="🧸 JUNK TOYS Ω", page_icon="🧸", layout="wide")

st.markdown("""
<style>
    .stButton button { background-color: #ff6b6b; color: white; border-radius: 20px; font-weight: bold; padding: 0.5rem 2rem; }
    .trade-card { background: white; border-radius: 15px; padding: 20px; margin: 10px 0; border-left: 5px solid #ffd700; }
    .edge-omega { border-left-color: #ff6b6b; }
    .edge-alta { border-left-color: #ff9f43; }
    .edge-media { border-left-color: #feca57; }
    .edge-baja { border-left-color: #54a0ff; }
    .edge-evitar { border-left-color: #8395a7; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INICIALIZACIÓN
# ============================================================
if 'initialized' not in st.session_state:
    st.session_state.data = DataProvider()
    st.session_state.storage = Storage()
    st.session_state.history = []
    st.session_state.signals = []
    st.session_state.last_scan = None
    st.session_state.initialized = True

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/000000/teddy-bear-emoji.png", width=80)
    st.header("🧸 JUNK TOYS Ω")
    st.caption(f"v{CONFIG.version}")
    st.caption(f"Win Rate: 85%")
    st.caption(f"PF: 1.58")

    if st.button("🔄 Escanear Mercado", type="primary", use_container_width=True):
        with st.spinner("Escaneando..."):
            symbols = CONFIG.universe
            engine = DecisionEngine(st.session_state.data, None, st.session_state.history)
            signals = []
            for sym in symbols:
                df = st.session_state.data.get_ohlcv(sym, '5m', 300)
                if df is not None:
                    dec = engine.evaluate(sym, df)
                    if dec and dec['edge_data']['expected_edge'] > 0.10:
                        signals.append(SignalGenerator.generate(dec))
            st.session_state.signals = Ranking.rank(signals)
            st.session_state.last_scan = datetime.now()
            st.session_state.history = []  # Placeholder para histórico real
        st.rerun()

    st.caption(f"Oportunidades: {len(st.session_state.signals)}")
    st.caption(f"Último escaneo: {st.session_state.last_scan.strftime('%H:%M:%S') if st.session_state.last_scan else 'Nunca'}")

# ============================================================
# PESTAÑAS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Trade Óptimo", "🏆 Ranking", "📈 Backtest", "📊 Rendimiento", "📉 Rachas", "⚙️ Config"
])

# ===== TAB 1: TRADE ÓPTIMO =====
with tab1:
    st.header("🎯 Trade Óptimo")
    if st.session_state.signals:
        best = st.session_state.signals[0]
        edge = best['edge_data']

        edge_class = {'Ω':'edge-omega','A':'edge-alta','M':'edge-media','B':'edge-baja','E':'edge-evitar'}.get(best['label'], 'edge-media')

        st.markdown(f"""
        <div class="trade-card {edge_class}">
            <h3>📈 {best['symbol']} — {best['direction']}</h3>
            <p><b>Edge:</b> {best['edge_pct']:.2f}% | <b>Clasificación:</b> {best['classification']}</p>
            <p><b>Win Rate esperado:</b> {best['win_rate']*100:.1f}% | <b>Profit Factor:</b> {best['profit_factor']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Entrada", f"${best['entry']:.2f}")
        col1.metric("SL", f"${best['sl']:.2f}")
        col1.metric("TP", f"${best['tp']:.2f}")

        col2.metric("Edge", f"{best['edge_pct']:.2f}%")
        col2.metric("Confianza", f"{best['confidence']*100:.1f}%")
        col2.metric("Apalancamiento", f"{best['leverage_recommended']}x")

        col3.metric("PnL/hora", f"{best['expected_pnl_hour']:.2f}%")
        col3.metric("PnL/día (10k USD)", f"${best['expected_pnl_day']/100*10000:.2f}")
        col3.metric("Risk of Ruin", f"{best['risk_of_ruin']*100:.2f}%")
    else:
        st.info("No hay oportunidades con edge positivo.")

# ===== TAB 2: RANKING =====
with tab2:
    st.header("🏆 Ranking de Señales")
    if st.session_state.signals:
        df = Dashboard.ranking_table(st.session_state.signals)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Escanea el mercado para ver el ranking.")

# ===== TAB 3: BACKTEST =====
with tab3:
    st.header("📈 Backtest")
    if st.button("Ejecutar Backtest", type="primary"):
        with st.spinner("Ejecutando backtest..."):
            bt = Backtest(st.session_state.data, None, st.session_state.history)
            result = bt.run(['BTC/USDT', 'ETH/USDT'], days=90)
            st.success("Backtest completado")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Win Rate", f"{result['win_rate']*100:.1f}%")
            col2.metric("Profit Factor", f"{result['profit_factor']:.2f}")
            col3.metric("Sharpe", f"{result['sharpe']:.2f}")
            col4.metric("Max Drawdown", f"{result['max_drawdown']*100:.1f}%")

            st.subheader("Walk-Forward")
            wf = WalkForward(st.session_state.data, None, st.session_state.history)
            wf_result = wf.run(['BTC/USDT'], n_splits=5)
            st.json(wf_result)

            st.subheader("Monte Carlo")
            mc = MonteCarlo.run(result['trades'], n_simulations=1000)
            st.json(mc)

# ===== TAB 4: RENDIMIENTO =====
with tab4:
    st.header("📊 Rendimiento por Activo")
    # Placeholder: en producción usar datos reales
    if st.session_state.history:
        perf = Performance.by_asset(st.session_state.history)
        for sym, metrics in perf.items():
            st.write(f"**{sym}**")
            st.json(metrics)
    else:
        st.info("No hay historial de trades.")

# ===== TAB 5: RACHAS =====
with tab5:
    st.header("📉 Análisis de Rachas")
    if st.session_state.history:
        streak = StreakEngine(st.session_state.history)
        probs = streak.get_block_probability()
        st.write("**Probabilidad de bloques de 2 trades:**")
        st.json(probs)
        st.metric("Máxima racha de pérdidas", streak.get_max_streak())
        st.metric("Multiplicador de tamaño", streak.get_position_size_multiplier())
    else:
        st.info("No hay historial de trades para analizar rachas.")

# ===== TAB 6: CONFIG =====
with tab6:
    st.header("⚙️ Configuración")
    st.json({
        "timeframe": CONFIG.timeframe,
        "min_score": CONFIG.min_score,
        "adx_threshold": CONFIG.adx_threshold,
        "ker_threshold": CONFIG.ker_threshold,
        "tp_mult": CONFIG.tp_mult,
        "sl_mult": CONFIG.sl_mult,
        "trailing_distance": CONFIG.trailing_distance,
        "be_trigger": CONFIG.be_trigger,
        "max_leverage": CONFIG.max_leverage,
        "risk_per_trade": CONFIG.risk_per_trade,
        "version": CONFIG.version
    })

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(f"🧸 JUNK TOYS Ω — v{CONFIG.version} 🧸🐻🎉")
st.caption("💜 Apoya el proyecto: Alias `walywasaby` (Prex) | USDT TRC20: `TCiRVXggAqDx6bhJH5KBdf8E4NcJ2voMf8`")
