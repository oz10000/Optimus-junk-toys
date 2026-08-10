# 🧸 JUNK TOYS Ω — Sistema Científico de Trading

**Versión:** 9.0.0  
**Estado:** Completo y funcional

## Descripción

Sistema de trading basado en **Expected Edge Score**, consenso Multi-Timeframe, análisis de rachas y optimización de parámetros mediante Walk-Forward y Monte Carlo.

## Características Principales

- **Expected Edge Score**: Rentabilidad esperada, no solo probabilidad de acierto.
- **Consenso Multi-Timeframe**: 9 timeframes con pesos optimizados.
- **Break Even técnico + estadístico**: Dos sistemas independientes que se comparan automáticamente.
- **Trailing Stop adaptativo**: Basado en ATR, volatilidad, ADX y régimen.
- **Análisis de rachas**: WW, WL, LW, LL; ajuste dinámico de tamaño.
- **Backtesting, Walk-Forward y Monte Carlo**: Validación científica completa.
- **Dashboard interactivo**: Streamlit con métricas en tiempo real.

## Instalación

```bash
git clone <repo>
cd junktoys-omega
pip install -r requirements.txt
streamlit run streamlit_app.py