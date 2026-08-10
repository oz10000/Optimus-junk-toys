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
from typing import List, Dict, Any

# ============================================================
# CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO)
# ============================================================
st.set_page_config(
    page_title="🧸 JUNK TOYS Ω — Firm Signals & Rachas",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# IMPORTACIONES CON MANEJO DE ERRORES
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
# DEFINIR PESTAÑAS (INMEDIATAMENTE)
# ============================================================
tabs = st.tabs([
    "📊 Estado General",
    "🎯 Último Trade",
    "📈 Sistema de Rachas",
    "⏱️ Predicción Temporal",
    "🚀 Próxima Oportunidad",
    "🏆 TOP 5 LONG",
    "⬇️ TOP 5 SHORT",
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
# FUNCIONES AUXILIARES DE SEGURIDAD
# ============================================================
def get_config_attr(name: str, default: Any = None) -> Any:
    """Obtiene un atributo de CONFIG con fallback seguro."""
    return getattr(CONFIG, name, default)

def safe_format_timestamp(ts) -> str:
    """Convierte timestamp a string seguro, sea datetime o string."""
    if ts is None:
        return "N/A"
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d %H:%M")
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return ts[:16] if len(ts) >= 16 else ts
    return str(ts)

def get_top_signals(signals: List[Dict], direction: str, n: int = 5) -> List[Dict]:
    """Retorna las N mejores señales de una dirección específica (LONG/SHORT)."""
    filtered = [s for s in signals if s.get('direction') == direction]
    sorted_signals = sorted(filtered, key=lambda x: x.get('edge', 0), reverse=True)
    return sorted_signals[:n]

def create_dummy_signal(direction: str = 'LONG') -> Dict:
    """Crea una señal dummy para rellenar el TOP N cuando no hay señales reales."""
    return {
        'symbol': '---',
        'direction': direction,
        'expected_edge_pct': 0,
        'score': 0,
        'confidence': 0,
        'expected_profit_factor': 1.0,
        'shun_toy_score': 0,
        'approved': False,
        'classification': 'Sin señal',
        'regime': 'Normal',
        'volatility': 0,
        'entry_price': 0,
        'stop_loss': 0,
        'take_profit': 0,
        'break_even_technical': 0,
        'break_even_statistical': 0,
        'trailing_stop': {'activation': 0, 'distance': 0, 'protected_gain': 0},
        'leverage_recommended': 1,
        'leverage_max': 1,
        'time_since_last_trade': 0,
        'time_to_next_trade_expected': 0,
        'time_to_tp_expected': 0,
        'entry_range': {'low': 0, 'high': 0},
        'streak_status': {},
        'temporal_confidence': 0,
        'probability': 0,
        'edge': 0,
        'confidence': 0,
        'consensus_mtf': 0,
        'consensus_direction': 'NEUTRAL',
        'win_rate_expected': 0,
        'profit_factor_expected': 1.0,
        'risk_of_ruin': 1.0,
        'expectancy': 0,
        'shun_toy_level': 0,
        'min_protected_gain': 0,
    }

# ============================================================
# INICIALIZACIÓN DE SESIÓN
# ============================================================
if 'initialized' not in st.session_state:
    st.session_state.data = DataProvider()
    st.session_state.storage = Storage()
    st.session_state.history = []
    st.session_state.signals = []
    st.session_state.last_scan = None
    st.session_state.initialized = True

# ============================================================
# FUNCIONES PRINCIPALES
# ============================================================
def ensure_history():
    """Asegura que el historial tenga al menos 2 trades, ejecutando backtest si es necesario."""
    if len(st.session_state.history) >= 2:
        return

    stored = st.session_state.storage.load('history')
    if stored and len(stored) >= 2:
        st.session_state.history = stored
        return

    with st.spinner("🔄 Reconstruyendo historial mediante backtest..."):
        symbols = get_config_attr('universe', ['BTC/USDT', 'ETH/USDT'])
        backtest_days = get_config_attr('BACKTEST_DAYS', 90)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=backtest_days)

        data_provider = st.session_state.data
        engine = DecisionEngine(data_provider, None, [])
        backtest = Backtest(data_provider, engine)

        try:
            result = backtest.run(symbols, start_date, end_date, timeframe='5m')
            trades = result.get('trades', [])
            if len(trades) >= 2:
                st.session_state.history = trades
                st.session_state.storage.save('history', trades)
                st.success(f"✅ Historial reconstruido con {len(trades)} trades reales.")
            else:
                st.warning("⚠️ No se pudieron generar trades reales. El motor temporal usará datos disponibles.")
        except Exception as e:
            st.error(f"❌ Error en backtest automático: {str(e)}")
            st.info("ℹ️ El motor temporal funcionará con el historial disponible, si existe.")

def run_scan():
    """Escanea el mercado y actualiza las señales."""
    try:
        symbols = get_config_attr('universe', ['BTC/USDT', 'ETH/USDT'])
        engine = DecisionEngine(st.session_state.data, None, st.session_state.history)
        signals = []
        timeframe = get_config_attr('TIMEFRAME', '5m')

        for sym in symbols:
            df = st.session_state.data.get_ohlcv(sym, timeframe, 500)
            if df is not None and not df.empty:
                dec = engine.evaluate(sym, df)
                if dec is not None:
                    signal = SignalGenerator.generate(dec)
                    if signal is not None:
                        signals.append(signal)

        st.session_state.signals = Ranking.rank(signals)
        st.session_state.last_scan = datetime.now()

        approved = sum(1 for s in st.session_state.signals if s.get('approved', False))
        total = len(st.session_state.signals)
        st.success(f"✅ Escaneo: {total} señales ({approved} aprobadas, {total - approved} desaprobadas)")
    except Exception as e:
        st.error(f"❌ Error en el escaneo: {str(e)}")
        st.session_state.signals = []

# ============================================================
# EJECUTAR ENSURE_HISTORY AL INICIO
# ============================================================
ensure_history()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/000000/teddy-bear-emoji.png", width=80)
    st.header("🧸 JUNK TOYS Ω")
    st.caption(f"v{get_config_attr('version', '?')}")

    # Modo seguro con fallback
    firm_mode = get_config_attr('FIRM_MODE', False)
    mode_text = "🔥 FIRM SIGNALS (94% Win Rate)" if firm_mode else "📊 Modo General (86% Win Rate)"
    st.caption(f"Modo: {mode_text}")
    st.caption(f"Activos: {len(get_config_attr('universe', []))}")

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

    # Mostrar TOP 5 en sidebar (usando la función auxiliar)
    if st.session_state.signals:
        st.divider()
        st.subheader("🏆 TOP 5 GENERAL")
        top5 = sorted(st.session_state.signals, key=lambda x: x.get('edge', 0), reverse=True)[:5]
        for i, s in enumerate(top5, 1):
            approved = "✅" if s.get('approved', False) else "⚠️"
            st.caption(f"{i}. {s.get('symbol', 'N/A')} {s.get('direction', '')} {approved}")

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
        col4.metric("Expected Edge", f"{best.get('expected_edge', 0)*100:.2f}%")
    else:
        col2.metric("Mejor Señal", "Ninguna")
        col3.metric("Dirección", "--")
        col4.metric("Expected Edge", "--")

    st.caption(f"Modo: {'🔥 FIRM SIGNALS (94% Win Rate)' if get_config_attr('FIRM_MODE', False) else '📊 Modo General (86% Win Rate)'}")
    st.caption(f"Universo: {len(get_config_attr('universe', []))} activos monitorizados")

    if st.session_state.signals:
        col1, col2 = st.columns(2)
        with col1:
            directions = [s.get('direction', 'NEUTRAL') for s in st.session_state.signals]
            df_dir = pd.DataFrame({'Dirección': directions})
            fig1 = px.pie(df_dir, names='Dirección', title="Distribución por Dirección")
            st.plotly_chart(fig1, width='stretch')

        with col2:
            approved_status = ['Aprobada' if s.get('approved', False) else 'Desaprobada' for s in st.session_state.signals]
            df_app = pd.DataFrame({'Estado': approved_status})
            fig2 = px.pie(df_app, names='Estado', title="Señales Aprobadas vs Desaprobadas")
            st.plotly_chart(fig2, width='stretch')

    if st.session_state.signals:
        st.subheader("🏆 TOP 5 Oportunidades")
        top5 = sorted(st.session_state.signals, key=lambda x: x.get('edge', 0), reverse=True)[:5]
        df_top = pd.DataFrame([{
            '#': i+1,
            'Activo': s.get('symbol', 'N/A'),
            'Dirección': s.get('direction', 'N/A'),
            'Edge %': f"{s.get('expected_edge', 0)*100:.2f}%",
            'Aprobada': '✅' if s.get('approved', False) else '⚠️',
            'Clasificación': s.get('classification', 'N/A')
        } for i, s in enumerate(top5)])
        st.dataframe(df_top, width='stretch', hide_index=True)

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
        st.caption(f"Timestamp: {safe_format_timestamp(last.get('timestamp'))}")
        st.caption(f"Trailing Stop usado: {last.get('trailing_stop_used', 0)*100:.2f}%")
        st.caption(f"Break Even aplicado: {'✅ Sí' if last.get('break_even_applied', False) else '❌ No'}")
        st.caption(f"Motivo salida: {last.get('reason_exit', 'N/A')}")

        if len(st.session_state.history) >= 2:
            st.divider()
            st.subheader("📌 Penúltimo Trade")
            penultimate = st.session_state.history[-2]
            cols = st.columns(4)
            cols[0].metric("Activo", penultimate.get('symbol', 'N/A'))
            cols[1].metric("Dirección", penultimate.get('direction', 'N/A'))
            cols[2].metric("Resultado", f"{penultimate.get('pnl_pct', 0)*100:.2f}%")
            cols[3].metric("Ganador/Perdedor", "✅ Ganador" if penultimate.get('pnl_pct', 0) > 0 else "❌ Perdedor")
    else:
        st.info("No hay historial de trades aún.")
        st.caption("ℹ️ El sistema reconstruirá automáticamente el historial mediante backtest al iniciar.")

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

        st.subheader("📊 Probabilidades de Bloque (WW, WL, LW, LL)")
        probs = general.get('block_probabilities', {})
        if probs:
            df_probs = pd.DataFrame([probs])
            st.dataframe(df_probs.style.format("{:.1%}"), width='stretch')

        st.subheader("📈 Rachas por Activo")
        if analyzer.by_asset:
            data = []
            for asset, streaks in analyzer.by_asset.items():
                data.append({
                    'Activo': asset,
                    'Win Rate': streaks.get('win_rate', 0),
                    'Racha Ganancias': streaks.get('win_streaks', {}).get('current', 0),
                    'Racha Pérdidas': streaks.get('loss_streaks', {}).get('current', 0),
                    'Máx Ganancias': streaks.get('win_streaks', {}).get('max', 0),
                    'Máx Pérdidas': streaks.get('loss_streaks', {}).get('max', 0)
                })
            df_asset = pd.DataFrame(data)
            st.dataframe(df_asset.style.format({'Win Rate': '{:.1%}'}), width='stretch')

        st.subheader("⏰ Rachas por Horario (UTC)")
        if analyzer.by_hour:
            data = []
            for hour, streaks in analyzer.by_hour.items():
                data.append({
                    'Hora': f"{hour:02d}:00",
                    'Win Rate': streaks.get('win_rate', 0),
                    'Racha Ganancias': streaks.get('win_streaks', {}).get('current', 0),
                    'Racha Pérdidas': streaks.get('loss_streaks', {}).get('current', 0)
                })
            df_hour = pd.DataFrame(data)
            st.dataframe(df_hour.style.format({'Win Rate': '{:.1%}'}), width='stretch')

        st.subheader("🌊 Rachas por Régimen")
        if analyzer.by_regime:
            data = []
            for regime, streaks in analyzer.by_regime.items():
                data.append({
                    'Régimen': regime,
                    'Win Rate': streaks.get('win_rate', 0),
                    'Racha Ganancias': streaks.get('win_streaks', {}).get('current', 0),
                    'Racha Pérdidas': streaks.get('loss_streaks', {}).get('current', 0)
                })
            df_regime = pd.DataFrame(data)
            st.dataframe(df_regime.style.format({'Win Rate': '{:.1%}'}), width='stretch')

        st.subheader("🎯 ¿El trade actual está favorecido por la racha histórica?")
        if st.session_state.history:
            current_trade = st.session_state.history[-1]
            result = analyzer.is_favored_by_streak(current_trade)
            st.markdown(f"### {result['answer']}")
            st.caption(result['explanation'])
            col1, col2, col3 = st.columns(3)
            col1.metric("Racha pérdidas actual", result.get('current_loss_streak', 0))
            col2.metric("Racha ganancias actual", result.get('current_win_streak', 0))
            col3.metric("Probabilidad LL", f"{result.get('ll_probability', 0)*100:.1f}%")
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
        col1, col2 = st.columns(2)
        col1.metric("Error", f"{estimate.get('historical_error', 0)*100:.1f}%")
        col2.metric("Precisión", f"{estimate.get('precision', 0)*100:.1f}%")

        st.subheader("📊 Distribución de Intervalos")
        summary = dist.get_summary()

        col1, col2 = st.columns(2)
        col1.metric("Mediana", f"{summary.get('median', 0):.1f} min")
        col2.metric("Desviación Estándar", f"{summary.get('std', 0):.1f} min")

        col1, col2 = st.columns(2)
        col1.metric("Mínimo", f"{summary.get('min', 0):.1f} min")
        col2.metric("Máximo", f"{summary.get('max', 0):.1f} min")

        st.subheader("📋 Percentiles")
        percentiles = summary.get('percentiles', {})
        if percentiles:
            df_pct = pd.DataFrame([percentiles])
            st.dataframe(df_pct.style.format("{:.1f}"), width='stretch')

        elapsed = estimate.get('elapsed', 0)
        mean_interval = estimate.get('avg_interval', 45)
        if elapsed > mean_interval * 1.5:
            st.warning(f"⚠️ Han pasado {elapsed:.1f} minutos. Esto es {((elapsed/mean_interval)-1)*100:.0f}% más del tiempo medio.")
        elif elapsed > mean_interval:
            st.info(f"ℹ️ Han pasado {elapsed:.1f} min. Se espera señal pronto.")
        else:
            st.success(f"✅ Tiempo transcurrido: {elapsed:.1f} min ({(elapsed/mean_interval)*100:.0f}% del tiempo medio)")

        if st.session_state.signals:
            st.subheader("🔗 Relación con señales actuales")
            best = st.session_state.signals[0]
            next_trade_remaining = best.get('time_to_next_trade_expected', 0)
            st.metric("Tiempo estimado para próxima señal", f"{next_trade_remaining:.1f} min")
            st.caption(f"Confianza en la estimación: {best.get('temporal_confidence', 0)*100:.1f}%")
    else:
        st.info("Se necesitan al menos 2 trades para análisis temporal.")
        st.caption("ℹ️ El sistema reconstruirá automáticamente el historial mediante backtest al iniciar.")

# --- TAB 4: PRÓXIMA OPORTUNIDAD ESTIMADA ---
with tabs[4]:
    st.header("🚀 Próxima Oportunidad Estimada")
    if st.session_state.signals:
        st.subheader("📊 TOP 5 Oportunidades")
        top5 = sorted(st.session_state.signals, key=lambda x: x.get('edge', 0), reverse=True)[:5]
        for i, signal in enumerate(top5, 1):
            approved = signal.get('approved', False)
            status = "✅ APROBADA" if approved else "⚠️ DESAPROBADA"
            prob = signal.get('probability', 0)
            edge = signal.get('expected_edge', 0)
            direction = signal.get('direction', 'N/A')
            symbol = signal.get('symbol', 'N/A')
            st.caption(f"#{i} {symbol} | {direction} | Edge: {edge*100:.1f}% | Prob: {prob*100:.1f}% | {status}")

        best = st.session_state.signals[0]
        approved = best.get('approved', False)

        st.divider()
        st.subheader("🏆 Mejor Oportunidad")

        col1, col2, col3 = st.columns(3)
        col1.metric("Activo", best.get('symbol', 'N/A'))
        col2.metric("Dirección", best.get('direction', 'N/A'))
        col3.metric("Expected Edge", f"{best.get('expected_edge', 0)*100:.2f}%")

        col1, col2 = st.columns(2)
        col1.metric("Estado", "✅ Aprobada" if approved else "⚠️ Desaprobada")
        col2.metric("Confianza", f"{best.get('confidence', 0)*100:.1f}%")

        st.subheader("📋 Detalles de la Señal")
        cols = st.columns(4)
        cols[0].metric("Entry", f"${best.get('entry_price', 0):.2f}")
        cols[1].metric("SL", f"${best.get('stop_loss', 0):.2f}")
        cols[2].metric("TP", f"${best.get('take_profit', 0):.2f}")
        cols[3].metric("Apalancamiento", f"{best.get('leverage_recommended', 1):.1f}x")

        cols = st.columns(4)
        cols[0].metric("BE Técnico", f"{best.get('break_even_technical', 0)*100:.2f}%")
        cols[1].metric("BE Estadístico", f"{best.get('break_even_statistical', 0)*100:.2f}%")
        cols[2].metric("Trailing Activ.", f"{best.get('trailing_stop', {}).get('activation', 0)*100:.2f}%")
        cols[3].metric("Trailing Dist.", f"{best.get('trailing_stop', {}).get('distance', 0)*100:.2f}%")

        cols = st.columns(3)
        cols[0].metric("Rango entrada", f"{best.get('entry_range', {}).get('low', 0):.2f} - {best.get('entry_range', {}).get('high', 0):.2f}")
        cols[1].metric("Tiempo hasta TP estimado", f"{best.get('time_to_tp_expected', 0):.1f} min")
        cols[2].metric("Ganancia mínima protegida", f"{best.get('min_protected_gain', 0)*100:.2f}%")

        if len(st.session_state.history) >= 2:
            timing = TimingEngine(st.session_state.history)
            estimate = timing.estimate_next_trade()
            col1, col2 = st.columns(2)
            col1.metric("Tiempo restante esperado", f"{estimate.get('remaining_minutes', 0):.1f} min")
            col2.metric("Confianza Temporal", f"{estimate.get('confidence', 0)*100:.1f}%")
            st.caption(f"Precisión histórica: {estimate.get('precision', 0)*100:.1f}%")

        st.subheader("📊 Justificación Estadística")
        st.caption(f"""
        - **Win Rate Histórico**: {best.get('win_rate_expected', 0)*100:.1f}%
        - **Profit Factor**: {best.get('profit_factor_expected', 0):.2f}
        - **Confianza**: {best.get('confidence', 0)*100:.1f}%
        - **Régimen**: {best.get('regime', 'N/A')}
        - **Consenso MTF**: {best.get('consensus_mtf', 0):.2f}
        - **Consenso Dirección**: {best.get('consensus_direction', 'NEUTRAL')}
        - **Clasificación**: {best.get('classification', 'N/A')}
        - **ShunToy Level**: {best.get('shun_toy_level', 0):.1f}/10
        """)

        if approved:
            st.success("✅ **Oportunidad Aprobada**: Supera los umbrales de Edge y Confianza")
        else:
            edge = best.get('expected_edge', 0)
            conf = best.get('confidence', 0)
            razones = []
            if edge <= 0.10:
                razones.append(f"Edge ({edge*100:.1f}%) ≤ umbral")
            if conf <= 0.40:
                razones.append(f"Confianza ({conf*100:.1f}%) ≤ 40%")
            st.warning(f"⚠️ **Oportunidad Desaprobada**: {', '.join(razones) if razones else 'No supera umbrales'}")
    else:
        st.info("No hay oportunidades disponibles. Ejecuta un escaneo.")

# --- TAB 5: TOP 5 LONG ---
with tabs[5]:
    st.header("🏆 TOP 5 LONG")
    signals = st.session_state.signals if st.session_state.signals else []

    # Obtener TOP 5 LONG usando la función auxiliar
    longs = get_top_signals(signals, 'LONG', 5)

    # Si no hay suficientes señales, rellenar con dummies
    while len(longs) < 5:
        longs.append(create_dummy_signal('LONG'))

    approved_count = sum(1 for s in longs if s.get('approved', False))
    st.caption(f"📊 {len(longs)} señales LONG mostradas ({approved_count} aprobadas, {len(longs) - approved_count} desaprobadas)")

    for i, signal in enumerate(longs, 1):
        with st.container():
            approved = signal.get('approved', False)
            status_emoji = "✅" if approved else "⚠️"
            status_text = "APROBADA" if approved else "DESAPROBADA"
            st.subheader(f"#{i} - {signal['symbol']} {status_emoji} {status_text}")

            cols = st.columns(5)
            cols[0].metric("Edge", f"{signal.get('expected_edge_pct', 0):.2f}%")
            cols[1].metric("Score", f"{signal.get('score', 0):.1f}")
            cols[2].metric("Confianza", f"{signal.get('confidence', 0)*100:.1f}%")
            cols[3].metric("PF Esperado", f"{signal.get('expected_profit_factor', 1.0):.2f}")
            cols[4].metric("ShunToy", f"{signal.get('shun_toy_score', 0):.1f}/10")

            st.caption(f"""
            **Entry:** {signal.get('entry_price', 0):.2f} | **SL:** {signal.get('stop_loss', 0):.2f} | **TP:** {signal.get('take_profit', 0):.2f}
            **Break Even:** Técnico {signal.get('break_even_technical', 0)*100:.2f}% | Estadístico {signal.get('break_even_statistical', 0)*100:.2f}%
            **Trailing:** Activación {signal.get('trailing_stop', {}).get('activation', 0)*100:.2f}% | Distancia {signal.get('trailing_stop', {}).get('distance', 0)*100:.2f}% | Ganancia protegida {signal.get('trailing_stop', {}).get('protected_gain', 0)*100:.2f}%
            **Apalancamiento:** {signal.get('leverage_recommended', 1):.1f}x (máx {signal.get('leverage_max', 1):.1f}x)
            **Régimen:** {signal.get('regime', 'Normal')} | **Consenso MTF:** {signal.get('consensus_mtf', 0):.2f}
            **Tiempo desde último trade:** {signal.get('time_since_last_trade', 0):.0f} min | **Próximo trade estimado:** {signal.get('time_to_next_trade_expected', 0):.0f} min
            **Tiempo hasta TP estimado:** {signal.get('time_to_tp_expected', 0):.1f} min
            **Rango entrada esperado:** {signal.get('entry_range', {}).get('low', 0):.2f} - {signal.get('entry_range', {}).get('high', 0):.2f}
            **Racha:** {signal.get('streak_status', {}).get('explanation', 'Sin datos')}
            **Confianza Temporal:** {signal.get('temporal_confidence', 0)*100:.1f}%
            **Probabilidad:** {signal.get('probability', 0)*100:.1f}%
            """)

            if approved:
                st.caption("✅ **Aprobada**: Edge > umbral del activo y Confianza > 40%")
            else:
                edge = signal.get('edge', 0)
                conf = signal.get('confidence', 0)
                razones = []
                if edge <= 0.10:
                    razones.append(f"Edge ({edge*100:.1f}%) ≤ umbral")
                if conf <= 0.40:
                    razones.append(f"Confianza ({conf*100:.1f}%) ≤ 40%")
                st.caption(f"⚠️ **Desaprobada**: {', '.join(razones) if razones else 'No supera umbrales'}")

# --- TAB 6: TOP 5 SHORT ---
with tabs[6]:
    st.header("⬇️ TOP 5 SHORT")
    signals = st.session_state.signals if st.session_state.signals else []

    # Obtener TOP 5 SHORT usando la función auxiliar
    shorts = get_top_signals(signals, 'SHORT', 5)

    # Si no hay suficientes señales, rellenar con dummies
    while len(shorts) < 5:
        shorts.append(create_dummy_signal('SHORT'))

    approved_count = sum(1 for s in shorts if s.get('approved', False))
    st.caption(f"📊 {len(shorts)} señales SHORT mostradas ({approved_count} aprobadas, {len(shorts) - approved_count} desaprobadas)")

    for i, signal in enumerate(shorts, 1):
        with st.container():
            approved = signal.get('approved', False)
            status_emoji = "✅" if approved else "⚠️"
            status_text = "APROBADA" if approved else "DESAPROBADA"
            st.subheader(f"#{i} - {signal['symbol']} {status_emoji} {status_text}")

            cols = st.columns(5)
            cols[0].metric("Edge", f"{signal.get('expected_edge_pct', 0):.2f}%")
            cols[1].metric("Score", f"{signal.get('score', 0):.1f}")
            cols[2].metric("Confianza", f"{signal.get('confidence', 0)*100:.1f}%")
            cols[3].metric("PF Esperado", f"{signal.get('expected_profit_factor', 1.0):.2f}")
            cols[4].metric("ShunToy", f"{signal.get('shun_toy_score', 0):.1f}/10")

            st.caption(f"""
            **Entry:** {signal.get('entry_price', 0):.2f} | **SL:** {signal.get('stop_loss', 0):.2f} | **TP:** {signal.get('take_profit', 0):.2f}
            **Break Even:** Técnico {signal.get('break_even_technical', 0)*100:.2f}% | Estadístico {signal.get('break_even_statistical', 0)*100:.2f}%
            **Trailing:** Activación {signal.get('trailing_stop', {}).get('activation', 0)*100:.2f}% | Distancia {signal.get('trailing_stop', {}).get('distance', 0)*100:.2f}% | Ganancia protegida {signal.get('trailing_stop', {}).get('protected_gain', 0)*100:.2f}%
            **Apalancamiento:** {signal.get('leverage_recommended', 1):.1f}x (máx {signal.get('leverage_max', 1):.1f}x)
            **Régimen:** {signal.get('regime', 'Normal')} | **Consenso MTF:** {signal.get('consensus_mtf', 0):.2f}
            **Tiempo desde último trade:** {signal.get('time_since_last_trade', 0):.0f} min | **Próximo trade estimado:** {signal.get('time_to_next_trade_expected', 0):.0f} min
            **Tiempo hasta TP estimado:** {signal.get('time_to_tp_expected', 0):.1f} min
            **Rango entrada esperado:** {signal.get('entry_range', {}).get('low', 0):.2f} - {signal.get('entry_range', {}).get('high', 0):.2f}
            **Racha:** {signal.get('streak_status', {}).get('explanation', 'Sin datos')}
            **Confianza Temporal:** {signal.get('temporal_confidence', 0)*100:.1f}%
            **Probabilidad:** {signal.get('probability', 0)*100:.1f}%
            """)

            if approved:
                st.caption("✅ **Aprobada**: Edge > umbral del activo y Confianza > 40%")
            else:
                edge = signal.get('edge', 0)
                conf = signal.get('confidence', 0)
                razones = []
                if edge <= 0.10:
                    razones.append(f"Edge ({edge*100:.1f}%) ≤ umbral")
                if conf <= 0.40:
                    razones.append(f"Confianza ({conf*100:.1f}%) ≤ 40%")
                st.caption(f"⚠️ **Desaprobada**: {', '.join(razones) if razones else 'No supera umbrales'}")

# --- TAB 7: SHUNTOY LEVEL ---
with tabs[7]:
    st.header("🎯 ShunToy Level")
    if st.session_state.signals:
        best = st.session_state.signals[0]
        edge_data = best.get('edge_data', {})
        market_data = {'regime': best.get('regime', 'Normal'), 'volatility': best.get('volatility', 0)}
        historical_data = {
            'profit_factor': best.get('profit_factor_expected', 1.0),
            'expectancy': best.get('expectancy', 0),
            'risk_of_ruin': best.get('risk_of_ruin', 1.0),
            'walk_forward_consistency': 0.7,
            'monte_carlo_stability': 0.6
        }
        shun = ShunToyLevel.compute(edge_data, market_data, historical_data)

        col1, col2 = st.columns(2)
        col1.metric("ShunToy Level", f"{shun['score']:.1f}/10")
        col2.metric("Nivel", shun['level'])

        st.caption(shun.get('interpretation', ''))

        st.subheader("📊 Componentes del ShunToy Level")
        components = shun.get('components', {})
        df_comp = pd.DataFrame([components]).T
        df_comp.columns = ['Score']
        st.dataframe(df_comp.style.format("{:.3f}"), width='stretch')

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(components.keys()),
            y=list(components.values()),
            marker_color='blue'
        ))
        fig.update_layout(
            title='Componentes del ShunToy Level',
            xaxis_title='Componente',
            yaxis_title='Score',
            template='plotly_dark'
        )
        st.plotly_chart(fig, width='stretch')
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

        st.subheader("📊 Componentes")
        components = result.get('components', {})
        df_comp = pd.DataFrame([components]).T
        df_comp.columns = ['Score']
        st.dataframe(df_comp.style.format("{:.3f}"), width='stretch')

        st.subheader("📋 Métricas")
        metrics = result.get('metrics', {})
        if metrics:
            cols = st.columns(4)
            cols[0].metric("Tiempo desde último trade", f"{metrics.get('elapsed_minutes', 0):.1f} min")
            cols[1].metric("Tiempo medio entre trades", f"{metrics.get('mean_interval', 0):.1f} min")
            cols[2].metric("Error histórico", f"{metrics.get('historical_error_pct', 0):.1f}%")
            cols[3].metric("Frecuencia diaria", f"{metrics.get('frequency_per_day', 0):.2f}")

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

        cols = st.columns(3)
        cols[0].metric("Expectancy", f"{metrics.get('expectancy', 0):.2f}%")
        cols[1].metric("Avg Win", f"{metrics.get('avg_win', 0):.2f}%")
        cols[2].metric("Avg Loss", f"{metrics.get('avg_loss', 0):.2f}%")

        st.subheader("📈 Rendimiento por Activo")
        by_asset = Performance.by_asset(st.session_state.history)
        if by_asset:
            df_asset = pd.DataFrame(by_asset).T
            df_asset = df_asset[['n_trades', 'win_rate', 'profit_factor', 'total_return', 'sharpe', 'max_drawdown']]
            st.dataframe(df_asset.style.format({
                'win_rate': '{:.1%}',
                'profit_factor': '{:.2f}',
                'total_return': '{:.2f}%',
                'sharpe': '{:.2f}',
                'max_drawdown': '{:.2%}'
            }), width='stretch')

        st.subheader("⏰ Rendimiento por Horario (UTC)")
        by_hour = Performance.by_hour(st.session_state.history)
        if by_hour:
            df_hour = pd.DataFrame(by_hour).T
            df_hour = df_hour[['n_trades', 'win_rate', 'profit_factor']]
            st.dataframe(df_hour.style.format({
                'win_rate': '{:.1%}',
                'profit_factor': '{:.2f}'
            }), width='stretch')

        st.subheader("🌊 Rendimiento por Régimen")
        by_regime = Performance.by_regime(st.session_state.history)
        if by_regime:
            df_regime = pd.DataFrame(by_regime).T
            df_regime = df_regime[['n_trades', 'win_rate', 'profit_factor']]
            st.dataframe(df_regime.style.format({
                'win_rate': '{:.1%}',
                'profit_factor': '{:.2f}'
            }), width='stretch')
    else:
        st.info("No hay historial de trades.")

# --- TAB 10: BACKTEST ---
with tabs[10]:
    st.header("🧪 Backtest")
    if st.button("Ejecutar Backtest", type="primary"):
        with st.spinner("Ejecutando backtest..."):
            bt = Backtest(st.session_state.data, DecisionEngine(st.session_state.data, None, st.session_state.history))
            result = bt.run(
                get_config_attr('universe', ['BTC/USDT', 'ETH/USDT']),
                datetime.now() - timedelta(days=get_config_attr('BACKTEST_DAYS', 90)),
                datetime.now()
            )
            st.session_state.backtest_result = result
            st.success("✅ Backtest completado")

    if st.session_state.get('backtest_result'):
        result = st.session_state.backtest_result
        trades = result.get('trades', [])
        metrics = Metrics.compute(trades) if trades else {}

        cols = st.columns(4)
        cols[0].metric("Total Return", f"{metrics.get('total_return', 0):.2f}%")
        cols[1].metric("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%")
        cols[2].metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")
        cols[3].metric("Sharpe", f"{metrics.get('sharpe', 0):.2f}")

        cols = st.columns(3)
        cols[0].metric("N° Trades", result.get('n_trades', 0))
        cols[1].metric("Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.1f}%")
        cols[2].metric("Calmar", f"{metrics.get('calmar', 0):.2f}")

        if trades:
            st.subheader(f"📋 Últimos 10 trades del backtest ({len(trades)} totales)")
            df_bt = pd.DataFrame(trades[-10:])
            cols_show = ['symbol', 'direction', 'entry_price', 'exit_price', 'pnl_pct', 'reason_exit']
            available = [c for c in cols_show if c in df_bt.columns]
            st.dataframe(df_bt[available].style.format({
                'pnl_pct': '{:.2%}',
                'entry_price': '${:.2f}',
                'exit_price': '${:.2f}'
            }), width='stretch')
    else:
        st.info("Presiona 'Ejecutar Backtest' para comenzar.")

# --- TAB 11: WALK-FORWARD ---
with tabs[11]:
    st.header("🔄 Walk-Forward")
    if st.button("Ejecutar Walk-Forward", type="primary"):
        with st.spinner("Ejecutando Walk-Forward (5 splits)..."):
            wf = WalkForward(st.session_state.data, None, st.session_state.history)
            result = wf.run(
                get_config_attr('universe', ['BTC/USDT', 'ETH/USDT']),
                train_days=180, test_days=90, n_splits=5
            )
            st.session_state.walkforward_result = result
            st.success("✅ Walk-Forward completado")

    if st.session_state.get('walkforward_result'):
        result = st.session_state.walkforward_result

        cols = st.columns(3)
        cols[0].metric("Avg Win Rate", f"{result.get('avg_win_rate', 0)*100:.1f}%")
        cols[1].metric("Avg PF", f"{result.get('avg_pf', 0):.2f}")
        cols[2].metric("Consistency", f"{result.get('consistency_score', 0)*100:.1f}%")

        st.subheader("📊 Splits")
        splits = result.get('splits', [])
        if splits:
            df_splits = pd.DataFrame(splits)
            df_splits = df_splits[['split', 'win_rate', 'profit_factor', 'sharpe', 'max_drawdown', 'n_trades']]
            st.dataframe(df_splits.style.format({
                'win_rate': '{:.1%}',
                'profit_factor': '{:.2f}',
                'sharpe': '{:.2f}',
                'max_drawdown': '{:.2%}'
            }), width='stretch')
    else:
        st.info("Presiona 'Ejecutar Walk-Forward' para comenzar.")

# --- TAB 12: MONTE CARLO ---
with tabs[12]:
    st.header("🎲 Monte Carlo")
    if st.button("Ejecutar Monte Carlo", type="primary"):
        with st.spinner("Ejecutando Monte Carlo (1000 simulaciones)..."):
            if st.session_state.history:
                result = MonteCarlo.run(st.session_state.history, n_simulations=1000)
                st.session_state.montecarlo_result = result
                st.success("✅ Monte Carlo completado")
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

        st.caption(f"Simulaciones: {result.get('n_simulations', 0)} | Trades usados: {result.get('n_trades_used', 0)}")

        capitals = result.get('all_final_capitals', [])
        if capitals:
            fig = px.histogram(capitals, nbins=50, title="Distribución de Capital Final")
            fig.update_layout(xaxis_title='Capital Final ($)', yaxis_title='Frecuencia')
            st.plotly_chart(fig, width='stretch')
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
        st.plotly_chart(fig, width='stretch')

        col1, col2, col3 = st.columns(3)
        col1.metric("Return Total", f"{equity[-1]:.2f}%")
        col2.metric("Return Promedio", f"{np.mean(pnls)*100:.2f}%")
        col3.metric("Volatilidad", f"{np.std(pnls)*100:.2f}%")
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
        st.plotly_chart(fig, width='stretch')

        col1, col2, col3 = st.columns(3)
        col1.metric("Drawdown Máximo", f"{max(dd):.2f}%")
        col2.metric("Drawdown Actual", f"{dd[-1]:.2f}%")
        col3.metric("Drawdown Promedio", f"{np.mean(dd):.2f}%")

        st.subheader("📋 Top 5 Drawdowns")
        dd_sorted = sorted(dd, reverse=True)[:5]
        df_dd = pd.DataFrame({
            'Rank': list(range(1, 6)),
            'Drawdown %': [f"{d:.2f}%" for d in dd_sorted]
        })
        st.dataframe(df_dd, width='stretch')
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

        st.subheader("📊 Distribución de PnL")
        pnls = [t.get('pnl_pct', 0) for t in st.session_state.history]
        fig = px.histogram(pnls, nbins=20, title="Distribución de PnL")
        fig.update_layout(xaxis_title='PnL (%)', yaxis_title='Frecuencia')
        st.plotly_chart(fig, width='stretch')

        col1, col2, col3 = st.columns(3)
        col1.metric("PnL Promedio", f"{np.mean(pnls)*100:.2f}%")
        col2.metric("PnL Mediana", f"{np.median(pnls)*100:.2f}%")
        col3.metric("PnL Std", f"{np.std(pnls)*100:.2f}%")
    else:
        st.info("No hay historial de trades.")

# --- TAB 16: HISTORIAL COMPLETO ---
with tabs[16]:
    st.header("📋 Historial Completo de Señales")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        cols_to_show = ['symbol', 'direction', 'entry_price', 'exit_price', 'pnl_pct', 'duration_minutes', 'regime', 'reason_exit', 'timestamp']
        available_cols = [c for c in cols_to_show if c in df_history.columns]

        if 'timestamp' in df_history.columns:
            df_history['timestamp'] = df_history['timestamp'].apply(safe_format_timestamp)

        st.dataframe(df_history[available_cols].style.format({
            'pnl_pct': '{:.2%}',
            'entry_price': '${:.2f}',
            'exit_price': '${:.2f}'
        }), width='stretch')

        st.subheader("📊 Resumen del Historial")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Trades", len(df_history))
        if 'timestamp' in df_history.columns:
            try:
                min_ts = df_history['timestamp'].min()
                max_ts = df_history['timestamp'].max()
                col2.metric("Periodo", f"{min_ts} - {max_ts}")
            except:
                col2.metric("Periodo", "N/A")
        else:
            col2.metric("Periodo", "N/A")
        col3.metric("Activos", df_history['symbol'].nunique() if 'symbol' in df_history else 0)

        csv = df_history.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay historial de señales.")
