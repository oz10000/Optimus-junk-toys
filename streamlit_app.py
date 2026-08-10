# streamlit_app.py (SOLO SECCIONES MODIFICADAS)
# ... (imports y configuraciones iniciales iguales)

# ============================================================
# FUNCIÓN DE ESCANEO (MODIFICADA - NO FILTRA SEÑALES)
# ============================================================
def run_scan():
    """Escanea el mercado y actualiza las señales (TODAS las señales)."""
    try:
        symbols = CONFIG.universe
        engine = DecisionEngine(st.session_state.data, None, st.session_state.history)
        signals = []

        for sym in symbols:
            df = st.session_state.data.get_ohlcv(sym, '5m', 300)
            if df is not None and not df.empty:
                dec = engine.evaluate(sym, df)
                # Generar señal incluso si edge es bajo (NO filtrar)
                signal = SignalGenerator.generate(dec)
                if signal is not None:
                    signals.append(signal)

        # Ordenar todas las señales por edge (incluyendo las de bajo edge)
        st.session_state.signals = Ranking.rank(signals)
        st.session_state.last_scan = datetime.now()

        # Contar aprobadas vs desaprobadas
        approved = sum(1 for s in st.session_state.signals if s.get('edge', 0) > 0.10 and s.get('confidence', 0) > 0.40)
        total = len(st.session_state.signals)
        st.success(f"✅ Escaneo completado. {total} oportunidades encontradas ({approved} aprobadas, {total - approved} desaprobadas).")
    except Exception as e:
        st.error(f"❌ Error en el escaneo: {str(e)}")
        st.session_state.signals = []

# ===== TAB 6: TOP 3 LONG (MODIFICADO - MUESTRA APROBADAS Y DESAPROBADAS) =====
with tabs[5]:
    st.header("🏆 TOP 3 LONG")

    if st.session_state.signals:
        top = TopOpportunities.compute(st.session_state.signals)
        longs = top.get('top_long', [])

        if longs:
            # Mostrar resumen de aprobación
            approved_count = sum(1 for s in longs if s.get('approved', False))
            st.caption(f"📊 {len(longs)} señales LONG mostradas ({approved_count} aprobadas, {len(longs) - approved_count} desaprobadas)")

            for i, signal in enumerate(longs, 1):
                with st.container():
                    # Color según aprobación
                    approved = signal.get('approved', False)
                    status_emoji = "✅" if approved else "⚠️"
                    status_text = "APROBADA" if approved else "DESAPROBADA"
                    status_color = "green" if approved else "orange"

                    st.subheader(f"#{i} - {signal['symbol']} {status_emoji} {status_text}")

                    cols = st.columns(5)
                    cols[0].metric("Edge", f"{signal['expected_edge_pct']:.2f}%")
                    cols[1].metric("Score", f"{signal['score']:.1f}")
                    cols[2].metric("Confianza", f"{signal['confidence']*100:.1f}%")
                    cols[3].metric("PF Esperado", f"{signal['expected_profit_factor']:.2f}")
                    cols[4].metric("ShunToy", f"{signal['shun_toy_score']:.1f}/10")

                    st.caption(f"Régimen: {signal['regime']} | Volatilidad: {signal['volatility']*100:.2f}% | Clasificación: {signal['classification']} ({signal['label']})")

                    # Mostrar razón de aprobación/desaprobación
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
    else:
        st.info("No hay oportunidades disponibles. Ejecuta un escaneo.")

# ===== TAB 7: TOP 3 SHORT (MODIFICADO - MUESTRA APROBADAS Y DESAPROBADAS) =====
with tabs[6]:
    st.header("⬇️ TOP 3 SHORT")

    if st.session_state.signals:
        top = TopOpportunities.compute(st.session_state.signals)
        shorts = top.get('top_short', [])

        if shorts:
            # Mostrar resumen de aprobación
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
    else:
        st.info("No hay oportunidades disponibles. Ejecuta un escaneo.")

# ===== TAB 4: PREDICCIÓN TEMPORAL (MEJORADO) =====
with tabs[3]:
    st.header("⏱️ Predicción Temporal")

    if len(st.session_state.history) >= 2:
        timing = TimingEngine(st.session_state.history)
        dist = DistributionAnalyzer(st.session_state.history)

        estimate = timing.estimate_next_trade()

        # Métricas principales
        col1, col2, col3 = st.columns(3)
        col1.metric("⏰ Tiempo desde último trade", f"{estimate.get('elapsed', 0):.1f} min")
        col2.metric("📊 Tiempo medio entre trades", f"{estimate.get('avg_interval', 0):.1f} min")
        col3.metric("⏳ Tiempo restante esperado", f"{estimate.get('remaining_minutes', 0):.1f} min")

        # Intervalo de confianza
        st.subheader("📈 Intervalo de Confianza (10%-90%)")
        confidence_interval = estimate.get('interval_ci', (0, 0))
        st.metric("Rango estimado", f"{confidence_interval[0]:.1f} - {confidence_interval[1]:.1f} min")

        # Error histórico
        st.subheader("📉 Error Histórico de Predicción")
        st.metric("Error", f"{estimate.get('historical_error', 0)*100:.1f}%")

        # Distribución de intervalos
        st.subheader("📊 Distribución de Intervalos")
        summary = dist.get_summary()

        col1, col2 = st.columns(2)
        col1.metric("Mediana", f"{summary.get('median', 0):.1f} min")
        col2.metric("Desviación Estándar", f"{summary.get('std', 0):.1f} min")

        # Percentiles
        st.subheader("📋 Percentiles")
        percentiles = summary.get('percentiles', {})
        if percentiles:
            df_pct = pd.DataFrame([percentiles])
            st.dataframe(df_pct.style.format("{:.1f}"))

        # Mostrar el estado actual en relación a la predicción
        elapsed = estimate.get('elapsed', 0)
        mean_interval = estimate.get('avg_interval', 45)
        if elapsed > mean_interval * 1.5:
            st.warning(f"⚠️ Han pasado {elapsed:.1f} minutos desde el último trade. Esto es {((elapsed/mean_interval)-1)*100:.0f}% más del tiempo medio.")
        elif elapsed > mean_interval:
            st.info(f"ℹ️ Han pasado {elapsed:.1f} minutos. El tiempo medio es {mean_interval:.1f} min. Se espera señal pronto.")
        else:
            st.success(f"✅ Tiempo transcurrido: {elapsed:.1f} min ({(elapsed/mean_interval)*100:.0f}% del tiempo medio)")

        # Mostrar señales actuales y su relación con la predicción temporal
        if st.session_state.signals:
            st.subheader("🔗 Relación con señales actuales")
            best = st.session_state.signals[0]
            next_trade_remaining = best.get('next_trade_remaining', 0)
            st.metric("Tiempo estimado para próxima señal", f"{next_trade_remaining:.1f} min")
            st.caption(f"Confianza en la estimación: {best.get('next_trade_confidence', 0)*100:.1f}%")
    else:
        st.info("Se necesitan al menos 2 trades para análisis temporal.")
        st.caption("ℹ️ El sistema reconstruirá automáticamente el historial mediante backtest al iniciar.")

# ===== TAB 5: PRÓXIMA OPORTUNIDAD ESTIMADA (MEJORADO) =====
with tabs[4]:
    st.header("🚀 Próxima Oportunidad Estimada")

    if st.session_state.signals:
        # Mostrar todas las señales con su estado de aprobación
        st.subheader("📊 Ranking de Oportunidades")

        for i, signal in enumerate(st.session_state.signals[:10], 1):
            approved = signal.get('edge', 0) > 0.10 and signal.get('confidence', 0) > 0.40
            status = "✅ APROBADA" if approved else "⚠️ DESAPROBADA"
            st.caption(f"#{i} {signal.get('symbol', 'N/A')} | {signal.get('direction', 'N/A')} | Edge: {signal.get('edge_pct', 0):.1f}% | {status}")

        best = st.session_state.signals[0]
        approved = best.get('edge', 0) > 0.10 and best.get('confidence', 0) > 0.40

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

        # Mostrar razón de aprobación/desaprobación
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
