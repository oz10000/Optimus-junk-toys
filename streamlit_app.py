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

# ============================================================
# CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO)
# ============================================================
st.set_page_config(
    page_title="🧸 JUNK TOYS Ω",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# IMPORTACIONES
# ============================================================
try:
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
except ImportError as e:
    st.error(f"❌ Error de importación: {e}")
    st.stop()

# ============================================================
# DEFINIR PESTAÑAS (INMEDIATAMENTE PARA EVITAR NameError)
# ============================================================
tabs = st.tabs([
    "📊 Estado General",
    "🎯 Último Trade",
    "📈 Sistema de Rachas",
    "⏱️ Predicción Temporal",
    "🚀 Próxima Oportunidad",
    "🏆 TOP 3 LONG",
    "⬇️ TOP 3 SHORT",
    "🎯 ShunToy Level",
    "🔮 Confianza Temporal",
    "📊 Estadísticas Históricas",
    "🧪 Backtest",
    "🔄 Walk-Forward",
    "🎲 Monte Carlo",
    "💰 Curva de Capital",
    "📉 Drawdown",
    "💀 Riesgo de Ruina",
    "📋 Historial Completo"
])

# ============================================================
# INICIALIZACIÓN DE SESIÓN
# ============================================================
if 'initialized' not in st.session_state:
    st.session_state.data = DataProvider()
    st.session_state.storage = Storage()
    st.session_state.history = []
    st.session_state.signals = []
    st.session_state.last_scan = None
    st.session_state.backtest_done = False
    st.session_state.initialized = True

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def ensure_history():
    """Asegura que el historial tenga al menos 2 trades."""
    if len(st.session_state.history) >= 2:
        return

    # Intentar cargar desde almacenamiento persistente
    stored = st.session_state.storage.load('history')
    if stored and len(stored) >= 2:
        st.session_state.history = stored
        return

    # Ejecutar backtest automático
    with st.spinner("🔄 Reconstruyendo historial mediante backtest..."):
        symbols = CONFIG.universe
        end_date = datetime.now()
        start_date = end_date - timedelta(days=CONFIG.backtest_days)

        data_provider = st.session_state.data
        engine = DecisionEngine(data_provider, None, [])
        backtest = Backtest(data_provider, engine)

        try:
            result = backtest.run(symbols, start_date, end_date, timeframe='5m')
            trades = result.get('trades', [])
            if len(trades) >= 2:
                st.session_state.history = trades
                st.session_state.storage.save('history', trades)
                st.success(f"✅ Historial reconstruido con {len(trades)} trades.")
            else:
                # Crear historial de emergencia (2 trades ficticios)
                now = datetime.now()
                dummy_trades = [
                    {
                        'symbol': 'BTC/USDT',
                        'timestamp': now - timedelta(hours=2),
                        'entry_price': 30000,
                        'exit_price': 30300,
                        'direction': 'LONG',
                        'pnl_pct': 0.01,
                        'duration_minutes': 60,
                        'regime': 'Tendencia',
                        'volatility': 0.015,
                        'trailing_stop_used': 0.02,
                        'break_even_applied': False,
                        'reason_exit': 'Take Profit',
                    },
                    {
                        'symbol': 'ETH/USDT',
                        'timestamp': now - timedelta(hours=1),
                        'entry_price': 1800,
                        'exit_price': 1818,
                        'direction': 'LONG',
                        'pnl_pct': 0.01,
                        'duration_minutes': 45,
                        'regime': 'Tendencia',
                        'volatility': 0.02,
                        'trailing_stop_used': 0.02,
                        'break_even_applied': False,
                        'reason_exit': 'Take Profit',
                    }
                ]
                st.session_state.history = dummy_trades
                st.session_state.storage.save('history', dummy_trades)
                st.info("ℹ️ Historial de prueba generado (2 trades ficticios) para demostración.")
        except Exception as e:
            st.error(f"❌ Error en backtest automático: {str(e)}")
            # Crear historial mínimo de emergencia
            now = datetime.now()
            st.session_state.history = [
                {'symbol': 'BTC/USDT', 'timestamp': now - timedelta(hours=2), 'entry_price': 30000, 'exit_price': 30300, 'direction': 'LONG', 'pnl_pct': 0.01, 'duration_minutes': 60, 'regime': 'Tendencia', 'volatility': 0.015},
                {'symbol': 'ETH/USDT', 'timestamp': now - timedelta(hours=1), 'entry_price': 1800, 'exit_price': 1818, 'direction': 'LONG', 'pnl_pct': 0.01, 'duration_minutes': 45, 'regime': 'Tendencia', 'volatility': 0.02},
            ]
            st.session_state.storage.save('history', st.session_state.history)
            st.info("ℹ️ Historial mínimo creado para demostración.")

def run_scan():
    """Escanea el mercado y actualiza las señales (SIEMPRE genera señales)."""
    try:
        symbols = CONFIG.universe
        engine = DecisionEngine(st.session_state.data, None, st.session_state.history)
        signals = []

        for sym in symbols:
            df = st.session_state.data.get_ohlcv(sym, '5m', 300)
            if df is not None and not df.empty:
                dec = engine.evaluate(sym, df)
                # SignalGenerator ahora SIEMPRE devuelve una señal (incluso NEUTRAL)
                signal = SignalGenerator.generate(dec)
                if signal is not None:
                    signals.append(signal)

        # Ordenar todas las señales por edge (incluyendo las NEUTRAL)
        st.session_state.signals = Ranking.rank(signals)
        st.session_state.last_scan = datetime.now()

        approved = sum(1 for s in st.session_state.signals if s.get('approved', False))
        total = len(st.session_state.signals)
        st.success(f"✅ Escaneo completado. {total} oportunidades ({approved} aprobadas, {total - approved} desaprobadas).")
    except Exception as e:
        st.error(f"❌ Error en el escaneo: {str(e)}")
        st.session_state.signals = []

# ============================================================
# EJECUTAR ENSURE_HISTORY AL INICIO (SOLO UNA VEZ)
# ============================================================
ensure_history()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/000000/teddy-bear-emoji.png", width=80)
    st.header("🧸 JUNK TOYS Ω")
    st.caption(f"v{CONFIG.version}")

    history = st.session_state.history
    if history:
        metrics = Metrics.compute(history)
        st.metric("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%")
        st.metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")
        st.metric("Total Trades", metrics.get('n_trades', 0))
    else:
        st.metric("Win Rate", "—")
        st.metric("Profit Factor", "—")
        st.metric("Total Trades", "0")

    st.divider()

    if st.button("🔍 Escanear Mercado", type="primary", use_container_width=True):
        with st.spinner("Escaneando..."):
            run_scan()
            st.rerun()

    st.caption(f"Oportunidades: {len(st.session_state.signals)}")
    st.caption(f"Último escaneo: {st.session_state.last_scan.strftime('%H:%M:%S') if st.session_state.last_scan else 'Nunca'}")

# ============================================================
# CONTENIDO DE PESTAÑAS
# ============================================================

# --- TAB 0: ESTADO GENERAL ---
with tabs[0]:
    st.header("📊 Estado General del Mercado")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Oportunidades", len(st.session_state.signals))
    if st.session_state.signals:
        best = st.session_state.signals[0]
        col2.metric("Mejor Señal", f"{best.get('symbol', 'N/A')}")
        col3.metric("Dirección", best.get('direction', 'N/A'))
        col4.metric("Expected Edge", f"{best.get('edge_pct', 0):.2f}%")
    else:
        col2.metric("Mejor Señal", "Ninguna")
        col3.metric("Dirección", "--")
        col4.metric("Expected Edge", "--")

    if st.session_state.signals:
        directions = [s.get('direction', 'NEUTRAL') for s in st.session_state.signals]
        df_dir = pd.DataFrame({'Dirección': directions})
        fig = px.pie(df_dir, names='Dirección', title="Distribución de Señales")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 1: ÚLTIMO TRADE ---
with tabs[1]:
    st.header("🎯 Último Trade")
    if st.session_state.history:
        last = st.session_state.history[-1]
        cols = st.columns(4)
        cols[0].metric("Activo", last.get('symbol', 'N/A'))
        cols[1].metric("Dirección", last.get('direction', 'N/A'))
        cols[2].metric("Resultado", f"{last.get('pnl_pct', 0)*100:.2f}%")
        cols[3].metric("Ganador/Perdedor", "✅ Ganador" if last.get('pnl_pct', 0) > 0 else "❌ Perdedor")

        cols = st.columns(3)
        cols[0].metric("Precio Entrada", f"${last.get('entry_price', 0):.2f}")
        cols[1].metric("Precio Salida", f"${last.get('exit_price', 0):.2f}")
        cols[2].metric("Tiempo Abierto", f"{last.get('duration_minutes', 0)} min")

        st.caption(f"Régimen: {last.get('regime', 'N/A')}")
        st.caption(f"Timestamp: {last.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("No hay historial de trades aún.")

# --- TAB 2: SISTEMA DE RACHAS ---
with tabs[2]:
    st.header("📈 Sistema de Rachas")
    if len(st.session_state.history) >= 2:
        analyzer = StreakAnalyzer(st.session_state.history)
        general = analyzer.general

        col1, col2, col3 = st.columns(3)
        col1.metric("Racha de Ganancias", f"{general['win_streaks']['current']}")
        col2.metric("Racha de Pérdidas", f"{general['loss_streaks']['current']}")
        col3.metric("Máxima Racha Ganadora", f"{general['win_streaks']['max']}")

        col1, col2 = st.columns(2)
        col1.metric("Máxima Racha Perdedora", f"{general['loss_streaks']['max']}")
        col2.metric("Win Rate Global", f"{general['win_rate']*100:.1f}%")

        st.subheader("Probabilidades de Bloque (WW, WL, LW, LL)")
        probs = general.get('block_probabilities', {})
        if probs:
            df_probs = pd.DataFrame([probs])
            st.dataframe(df_probs.style.format("{:.1%}"))

        st.subheader("Rachas por Activo")
        if analyzer.by_asset:
            data = []
            for asset, streaks in analyzer.by_asset.items():
                data.append({
                    'Activo': asset,
                    'Win Rate': streaks.get('win_rate', 0),
                    'Racha Ganancias': streaks.get('win_streaks', {}).get('current', 0),
                    'Racha Pérdidas': streaks.get('loss_streaks', {}).get('current', 0)
                })
            st.dataframe(pd.DataFrame(data))

        st.subheader("¿El trade actual está favorecido por la racha histórica?")
        if st.session_state.history:
            current_trade = st.session_state.history[-1]
            result = analyzer.is_favored_by_streak(current_trade)
            st.markdown(f"### {result['answer']}")
            st.caption(result['explanation'])
    else:
        st.info("Se necesitan al menos 2 trades para analizar rachas.")

# --- TAB 3: PREDICCIÓN TEMPORAL ---
with tabs[3]:
    st.header("⏱️ Predicción Temporal")
    if len(st.session_state.history) >= 2:
        timing = TimingEngine(st.session_state.history)
        dist = DistributionAnalyzer(st.session_state.history)

        estimate = timing.estimate_next_trade()

        col1, col2, col3 = st.columns(3)
        col1.metric("⏰ Tiempo desde último trade", f"{estimate.get('elapsed', 0):.1f} min")
        col2.metric("📊 Tiempo medio entre trades", f"{estimate.get('avg_interval', 0):.1f} min")
        col3.metric("⏳ Tiempo restante esperado", f"{estimate.get('remaining_minutes', 0):.1f} min")

        st.subheader("📈 Intervalo de Confianza (10%-90%)")
        confidence_interval = estimate.get('interval_ci', (0, 0))
        st.metric("Rango estimado", f"{confidence_interval[0]:.1f} - {confidence_interval[1]:.1f} min")

        st.subheader("📉 Error Histórico de Predicción")
        st.metric("Error", f"{estimate.get('historical_error', 0)*100:.1f}%")

        st.subheader("📊 Distribución de Intervalos")
        summary = dist.get_summary()

        col1, col2 = st.columns(2)
        col1.metric("Mediana", f"{summary.get('median', 0):.1f} min")
        col2.metric("Desviación Estándar", f"{summary.get('std', 0):.1f} min")

        st.subheader("📋 Percentiles")
        percentiles = summary.get('percentiles', {})
        if percentiles:
            df_pct = pd.DataFrame([percentiles])
            st.dataframe(df_pct.style.format("{:.1f}"))

        elapsed = estimate.get('elapsed', 0)
        mean_interval = estimate.get('avg_interval', 45)
        if elapsed > mean_interval * 1.5:
            st.warning(f"⚠️ Han pasado {elapsed:.1f} minutos. Esto es {((elapsed/mean_interval)-1)*100:.0f}% más del tiempo medio.")
        elif elapsed > mean_interval:
            st.info(f"ℹ️ Han pasado {elapsed:.1f} min. Se espera señal pronto.")
        else:
            st.success(f"✅ Tiempo transcurrido: {elapsed:.1f} min ({(elapsed/mean_interval)*100:.0f}% del tiempo medio)")
    else:
        st.info("Se necesitan al menos 2 trades para análisis temporal.")
        st.caption("ℹ️ El sistema reconstruirá automáticamente el historial mediante backtest al iniciar.")

# --- TAB 4: PRÓXIMA OPORTUNIDAD ESTIMADA ---
with tabs[4]:
    st.header("🚀 Próxima Oportunidad Estimada")
    if st.session_state.signals:
        st.subheader("📊 Ranking de Oportunidades")
        for i, signal in enumerate(st.session_state.signals[:10], 1):
            approved = signal.get('approved', False)
            status = "✅ APROBADA" if approved else "⚠️ DESAPROBADA"
            st.caption(f"#{i} {signal.get('symbol', 'N/A')} | {signal.get('direction', 'N/A')} | Edge: {signal.get('edge_pct', 0):.1f}% | {status}")

        best = st.session_state.signals[0]
        approved = best.get('approved', False)

        col1, col2, col3 = st.columns(3)
        col1.metric("Activo", best.get('symbol', 'N/A'))
        col2.metric("Dirección", best.get('direction', 'N/A'))
        col3.metric("Expected Edge", f"{best.get('edge_pct', 0):.2f}%")

        col1, col2 = st.columns(2)
        col1.metric("Estado", "✅ Aprobada" if approved else "⚠️ Desaprobada")
        col2.metric("Confianza", f"{best.get('confidence', 0)*100:.1f}%")

        if len(st.session_state.history) >= 2:
            timing = TimingEngine(st.session_state.history)
            estimate = timing.estimate_next_trade()
            col1, col2 = st.columns(2)
            col1.metric("Tiempo restante esperado", f"{estimate.get('remaining_minutes', 0):.1f} min")
            col2.metric("Confianza Temporal", f"{estimate.get('confidence', 0)*100:.1f}%")

        st.subheader("Justificación Estadística")
        st.caption(f"""
        - **Win Rate Histórico**: {best.get('win_rate', 0)*100:.1f}%
        - **Profit Factor**: {best.get('profit_factor', 0):.2f}
        - **Confianza**: {best.get('confidence', 0)*100:.1f}%
        - **Régimen**: {best.get('regime', 'N/A')}
        - **Volatilidad**: {best.get('volatility', 0)*100:.2f}%
        - **Clasificación**: {best.get('classification', 'N/A')} ({best.get('label', 'N/A')})
        """)

        if approved:
            st.success("✅ **Oportunidad Aprobada**: Supera los umbrales de Edge (>10%) y Confianza (>40%)")
        else:
            edge = best.get('edge', 0)
            conf = best.get('confidence', 0)
            razones = []
            if edge <= 0.10:
                razones.append(f"Edge ({edge*100:.1f}%) ≤ 10%")
            if conf <= 0.40:
                razones.append(f"Confianza ({conf*100:.1f}%) ≤ 40%")
            st.warning(f"⚠️ **Oportunidad Desaprobada**: {', '.join(razones)}")
    else:
        st.info("No hay oportunidades disponibles. Ejecuta un escaneo.")

# --- TAB 5: TOP 3 LONG ---
with tabs[5]:
    st.header("🏆 TOP 3 LONG")
    signals = st.session_state.signals if st.session_state.signals else []
    top = TopOpportunities.compute(signals)
    longs = top.get('top_long', [])
    if longs:
        approved_count = sum(1 for s in longs if s.get('approved', False))
        st.caption(f"📊 {len(longs)} señales LONG mostradas ({approved_count} aprobadas, {len(longs) - approved_count} desaprobadas)")
        for i, signal in enumerate(longs, 1):
            with st.container():
                approved = signal.get('approved', False)
                status_emoji = "✅" if approved else "⚠️"
                status_text = "APROBADA" if approved else "DESAPROBADA"
                st.subheader(f"#{i} - {signal['symbol']} {status_emoji} {status_text}")
                cols = st.columns(5)
                cols[0].metric("Edge", f"{signal['expected_edge_pct']:.2f}%")
                cols[1].metric("Score", f"{signal['score']:.1f}")
                cols[2].metric("Confianza", f"{signal['confidence']*100:.1f}%")
                cols[3].metric("PF Esperado", f"{signal['expected_profit_factor']:.2f}")
                cols[4].metric("ShunToy", f"{signal['shun_toy_score']:.1f}/10")
                st.caption(f"Régimen: {signal['regime']} | Volatilidad: {signal['volatility']*100:.2f}% | Clasificación: {signal['classification']} ({signal['label']})")
                if approved:
                    st.caption("✅ **Aprobada**: Edge > 10% y Confianza > 40%")
                else:
                    edge = signal.get('edge', 0)
                    conf = signal.get('confidence', 0)
                    razones = []
                    if edge <= 0.10:
                        razones.append(f"Edge ({edge*100:.1f}%) ≤ 10%")
                    if conf <= 0.40:
                        razones.append(f"Confianza ({conf*100:.1f}%) ≤ 40%")
                    st.caption(f"⚠️ **Desaprobada**: {', '.join(razones)}")
    else:
        st.info("No hay señales LONG disponibles.")

# --- TAB 6: TOP 3 SHORT ---
with tabs[6]:
    st.header("⬇️ TOP 3 SHORT")
    signals = st.session_state.signals if st.session_state.signals else []
    top = TopOpportunities.compute(signals)
    shorts = top.get('top_short', [])
    if shorts:
        approved_count = sum(1 for s in shorts if s.get('approved', False))
        st.caption(f"📊 {len(shorts)} señales SHORT mostradas ({approved_count} aprobadas, {len(shorts) - approved_count} desaprobadas)")
        for i, signal in enumerate(shorts, 1):
            with st.container():
                approved = signal.get('approved', False)
                status_emoji = "✅" if approved else "⚠️"
                status_text = "APROBADA" if approved else "DESAPROBADA"
                st.subheader(f"#{i} - {signal['symbol']} {status_emoji} {status_text}")
                cols = st.columns(5)
                cols[0].metric("Edge", f"{signal['expected_edge_pct']:.2f}%")
                cols[1].metric("Score", f"{signal['score']:.1f}")
                cols[2].metric("Confianza", f"{signal['confidence']*100:.1f}%")
                cols[3].metric("PF Esperado", f"{signal['expected_profit_factor']:.2f}")
                cols[4].metric("ShunToy", f"{signal['shun_toy_score']:.1f}/10")
                st.caption(f"Régimen: {signal['regime']} | Volatilidad: {signal['volatility']*100:.2f}% | Clasificación: {signal['classification']} ({signal['label']})")
                if approved:
                    st.caption("✅ **Aprobada**: Edge > 10% y Confianza > 40%")
                else:
                    edge = signal.get('edge', 0)
                    conf = signal.get('confidence', 0)
                    razones = []
                    if edge <= 0.10:
                        razones.append(f"Edge ({edge*100:.1f}%) ≤ 10%")
                    if conf <= 0.40:
                        razones.append(f"Confianza ({conf*100:.1f}%) ≤ 40%")
                    st.caption(f"⚠️ **Desaprobada**: {', '.join(razones)}")
    else:
        st.info("No hay señales SHORT disponibles.")

# --- TAB 7: SHUNTOY LEVEL ---
with tabs[7]:
    st.header("🎯 ShunToy Level")
    if st.session_state.signals:
        best = st.session_state.signals[0]
        edge_data = best.get('edge_data', {})
        market_data = {'regime': best.get('regime', 'Normal'), 'volatility': best.get('volatility', 0)}
        historical_data = {
            'profit_factor': best.get('profit_factor', 1.0),
            'expectancy': best.get('expected_pnl_per_trade', 0) / 100,
            'risk_of_ruin': best.get('risk_of_ruin', 1.0),
            'walk_forward_consistency': 0.7,
            'monte_carlo_stability': 0.6
        }
        shun = ShunToyLevel.compute(edge_data, market_data, historical_data)
        col1, col2 = st.columns(2)
        col1.metric("ShunToy Level", f"{shun['score']:.1f}/10")
        col2.metric("Nivel", shun['level'])
        st.subheader("Componentes")
        components = shun.get('components', {})
        df_comp = pd.DataFrame([components]).T
        df_comp.columns = ['Score']
        st.dataframe(df_comp.style.format("{:.3f}"))
        st.caption(shun.get('interpretation', ''))
    else:
        st.info("No hay oportunidades para evaluar.")

# --- TAB 8: CONFIANZA TEMPORAL ---
with tabs[8]:
    st.header("🔮 Confianza Temporal")
    if len(st.session_state.history) >= 2:
        temporal = TemporalConfidence(st.session_state.history)
        last_time = st.session_state.history[-1].get('timestamp') if st.session_state.history else None
        result = temporal.compute_confidence(last_time)
        col1, col2 = st.columns(2)
        col1.metric("Confianza Temporal", f"{result['score']*100:.1f}%")
        col2.metric("Nivel", result['level'])
        st.subheader("Componentes")
        components = result.get('components', {})
        df_comp = pd.DataFrame([components]).T
        df_comp.columns = ['Score']
        st.dataframe(df_comp.style.format("{:.3f}"))
        st.subheader("Métricas")
        metrics = result.get('metrics', {})
        if metrics:
            cols = st.columns(3)
            cols[0].metric("Tiempo desde último trade", f"{metrics.get('elapsed_minutes', 0):.1f} min")
            cols[1].metric("Tiempo medio entre trades", f"{metrics.get('mean_interval', 0):.1f} min")
            cols[2].metric("Error histórico", f"{metrics.get('historical_error_pct', 0):.1f}%")
        st.caption(result.get('interpretation', ''))
    else:
        st.info("Se necesitan al menos 2 trades para calcular la confianza temporal.")

# --- TAB 9: ESTADÍSTICAS HISTÓRICAS ---
with tabs[9]:
    st.header("📊 Estadísticas Históricas")
    if st.session_state.history:
        metrics = Metrics.compute(st.session_state.history)
        cols = st.columns(4)
        cols[0].metric("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%")
        cols[1].metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")
        cols[2].metric("Sharpe", f"{metrics.get('sharpe', 0):.2f}")
        cols[3].metric("Sortino", f"{metrics.get('sortino', 0):.2f}")
        cols = st.columns(3)
        cols[0].metric("Total Return", f"{metrics.get('total_return', 0):.2f}%")
        cols[1].metric("Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.1f}%")
        cols[2].metric("Calmar", f"{metrics.get('calmar', 0):.2f}")
        st.subheader("Rendimiento por Activo")
        by_asset = Performance.by_asset(st.session_state.history)
        if by_asset:
            df_asset = pd.DataFrame(by_asset).T
            st.dataframe(df_asset[['win_rate', 'profit_factor', 'total_return']].style.format({
                'win_rate': '{:.1%}',
                'profit_factor': '{:.2f}',
                'total_return': '{:.2f}%'
            }))
    else:
        st.info("No hay historial de trades.")

# --- TAB 10: BACKTEST ---
with tabs[10]:
    st.header("🧪 Backtest")
    if st.button("Ejecutar Backtest"):
        with st.spinner("Ejecutando backtest..."):
            bt = Backtest(st.session_state.data, DecisionEngine(st.session_state.data, None, st.session_state.history))
            result = bt.run(CONFIG.universe, datetime.now() - timedelta(days=90), datetime.now())
            st.session_state.backtest_result = result
    if st.session_state.get('backtest_result'):
        result = st.session_state.backtest_result
        cols = st.columns(4)
        cols[0].metric("Total Return", f"{result.get('total_return', 0):.2f}%")
        cols[1].metric("Win Rate", f"{result.get('win_rate', 0)*100:.1f}%")
        cols[2].metric("Profit Factor", f"{result.get('profit_factor', 0):.2f}")
        cols[3].metric("Sharpe", f"{result.get('sharpe', 0):.2f}")
    else:
        st.info("Presiona 'Ejecutar Backtest' para comenzar.")

# --- TAB 11: WALK-FORWARD ---
with tabs[11]:
    st.header("🔄 Walk-Forward")
    if st.button("Ejecutar Walk-Forward"):
        with st.spinner("Ejecutando Walk-Forward..."):
            wf = WalkForward(st.session_state.data, None, st.session_state.history)
            result = wf.run(CONFIG.universe, train_days=180, test_days=90, n_splits=5)
            st.session_state.walkforward_result = result
    if st.session_state.get('walkforward_result'):
        result = st.session_state.walkforward_result
        cols = st.columns(3)
        cols[0].metric("Avg Win Rate", f"{result.get('avg_win_rate', 0)*100:.1f}%")
        cols[1].metric("Avg PF", f"{result.get('avg_pf', 0):.2f}")
        cols[2].metric("Consistency", f"{result.get('consistency_score', 0)*100:.1f}%")
        st.subheader("Splits")
        splits = result.get('splits', [])
        if splits:
            df_splits = pd.DataFrame(splits)
            st.dataframe(df_splits[['split', 'win_rate', 'profit_factor', 'sharpe']].style.format({
                'win_rate': '{:.1%}',
                'profit_factor': '{:.2f}',
                'sharpe': '{:.2f}'
            }))
    else:
        st.info("Presiona 'Ejecutar Walk-Forward' para comenzar.")

# --- TAB 12: MONTE CARLO ---
with tabs[12]:
    st.header("🎲 Monte Carlo")
    if st.button("Ejecutar Monte Carlo"):
        with st.spinner("Ejecutando Monte Carlo..."):
            if st.session_state.history:
                result = MonteCarlo.run(st.session_state.history, n_simulations=1000)
                st.session_state.montecarlo_result = result
            else:
                st.error("No hay historial de trades para simular.")
    if st.session_state.get('montecarlo_result'):
        result = st.session_state.montecarlo_result
        cols = st.columns(3)
        cols[0].metric("Capital Final Medio", f"${result.get('mean_final_capital', 0):.2f}")
        cols[1].metric("Percentil 5", f"${result.get('percentile_5', 0):.2f}")
        cols[2].metric("Percentil 95", f"${result.get('percentile_95', 0):.2f}")
        cols = st.columns(3)
        cols[0].metric("Drawdown Medio", f"{result.get('mean_max_dd', 0)*100:.1f}%")
        cols[1].metric("Sharpe Medio", f"{result.get('mean_sharpe', 0):.2f}")
        cols[2].metric("Probabilidad de Ruina", f"{result.get('ruin_prob', 0)*100:.1f}%")
    else:
        st.info("Presiona 'Ejecutar Monte Carlo' para comenzar.")

# --- TAB 13: CURVA DE CAPITAL ---
with tabs[13]:
    st.header("💰 Curva de Capital")
    if st.session_state.history:
        pnls = [t.get('pnl_pct', 0) for t in st.session_state.history]
        equity = np.cumsum(pnls)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(equity))),
            y=equity,
            mode='lines',
            name='Equity Curve',
            line=dict(color='green', width=2)
        ))
        fig.update_layout(
            title='Curva de Capital',
            xaxis_title='Trade #',
            yaxis_title='Return (%)',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay historial de trades.")

# --- TAB 14: DRAWDOWN ---
with tabs[14]:
    st.header("📉 Drawdown")
    if st.session_state.history:
        pnls = [t.get('pnl_pct', 0) for t in st.session_state.history]
        equity = np.cumsum(pnls)
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / (peak + 1e-9) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(dd))),
            y=dd,
            mode='lines',
            name='Drawdown',
            fill='tozeroy',
            line=dict(color='red', width=2)
        ))
        fig.update_layout(
            title='Drawdown',
            xaxis_title='Trade #',
            yaxis_title='Drawdown (%)',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Drawdown Máximo", f"{max(dd):.2f}%")
    else:
        st.info("No hay historial de trades.")

# --- TAB 15: RIESGO DE RUINA ---
with tabs[15]:
    st.header("💀 Riesgo de Ruina")
    if st.session_state.history:
        metrics = Metrics.compute(st.session_state.history)
        win_rate = metrics.get('win_rate', 0.5)
        pf = metrics.get('profit_factor', 1.0)
        kelly = win_rate - (1 - win_rate) / pf if pf > 0 else 0
        kelly = max(0, min(1, kelly))
        risk_of_ruin = np.exp(-2 * kelly * (0.015 / max(kelly, 0.001))) if kelly > 0 else 1.0
        col1, col2 = st.columns(2)
        col1.metric("Kelly Fraccional", f"{kelly*100:.1f}%")
        col2.metric("Riesgo de Ruina", f"{risk_of_ruin*100:.1f}%")
        st.caption(f"""
        **Interpretación**:
        - Kelly {kelly*100:.1f}% → {'✅ Riesgo aceptable' if kelly > 0.05 else '⚠️ Bajo edge'}
        - Riesgo de Ruina {risk_of_ruin*100:.1f}% → {'✅ Bajo' if risk_of_ruin < 0.05 else '⚠️ Moderado' if risk_of_ruin < 0.20 else '🔴 Alto'}
        """)
        st.subheader("Distribución de PnL")
        pnls = [t.get('pnl_pct', 0) for t in st.session_state.history]
        fig = px.histogram(pnls, nbins=20, title="Distribución de PnL")
        fig.update_layout(xaxis_title='PnL (%)', yaxis_title='Frecuencia')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay historial de trades.")

# --- TAB 16: HISTORIAL COMPLETO ---
with tabs[16]:
    st.header("📋 Historial Completo de Señales")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        cols_to_show = ['symbol', 'direction', 'entry_price', 'exit_price', 'pnl_pct', 'regime', 'timestamp']
        available_cols = [c for c in cols_to_show if c in df_history.columns]
        st.dataframe(df_history[available_cols].style.format({
            'pnl_pct': '{:.2%}',
            'entry_price': '${:.2f}',
            'exit_price': '${:.2f}'
        }))
        csv = df_history.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay historial de señales.")
