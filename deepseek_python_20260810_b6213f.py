# dashboard.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict

class Dashboard:
    """Visualización de métricas y rendimiento."""

    @staticmethod
    def equity_curve(equity: List[float]) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(equity))),
            y=equity,
            mode='lines',
            name='Equity',
            line=dict(color='#2ecc71')
        ))
        fig.update_layout(title='Curva de Capital', xaxis_title='Trade', yaxis_title='PnL %')
        return fig

    @staticmethod
    def drawdown(drawdowns: List[float]) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(drawdowns))),
            y=drawdowns,
            mode='lines',
            name='Drawdown',
            line=dict(color='#e74c3c'),
            fill='tozeroy'
        ))
        fig.update_layout(title='Drawdown', xaxis_title='Trade', yaxis_title='Drawdown %')
        return fig

    @staticmethod
    def heatmap_by_hour(data: Dict[int, Dict]) -> go.Figure:
        """Heatmap de Win Rate por hora."""
        hours = sorted(data.keys())
        win_rates = [data[h].get('win_rate', 0) for h in hours]
        df = pd.DataFrame({'Hora': hours, 'Win Rate': win_rates})
        fig = px.bar(df, x='Hora', y='Win Rate', title='Win Rate por Hora')
        fig.update_layout(yaxis_tickformat='.0%')
        return fig

    @staticmethod
    def ranking_table(signals: List[Dict]) -> pd.DataFrame:
        rows = []
        for i, s in enumerate(signals[:10]):
            rows.append({
                'Pos': i+1,
                'Activo': s['symbol'],
                'Dirección': s['direction'],
                'Edge': f"{s['edge']*100:.2f}%",
                'Clasificación': s['classification'],
                'Confianza': f"{s['confidence']*100:.1f}%",
                'Win Rate': f"{s['win_rate']*100:.1f}%',
                'PF': f"{s['profit_factor']:.2f}",
                'PnL/hora': f"{s['expected_pnl_hour']:.2f}%"
            })
        return pd.DataFrame(rows)