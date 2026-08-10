import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import DataLoader

class Dashboard:
    def __init__(self):
        self.data_loader = DataLoader()
        self.df = self.data_loader.load_data()
    
    def render(self):
        st.sidebar.header("Filtros")
        categorias = self.df['categoria'].unique() if 'categoria' in self.df.columns else []
        categoria_seleccionada = st.sidebar.selectbox("Selecciona categoría", categorias)
        
        if 'fecha' in self.df.columns:
            fecha_min = self.df['fecha'].min()
            fecha_max = self.df['fecha'].max()
            fecha_rango = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max])
        
        df_filtrado = self.df
        if categoria_seleccionada:
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_seleccionada]
        
        st.subheader("Métricas generales")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total registros", len(df_filtrado))
        col2.metric("Categorías", df_filtrado['categoria'].nunique())
        col3.metric("Valor total", f"${df_filtrado['valor'].sum():,.2f}")
        
        fig = px.bar(df_filtrado, x='categoria', y='valor', title="Valor por categoría")
        st.plotly_chart(fig, use_container_width=True)   # <-- Corregido (coma añadida)
        
        st.subheader("Datos")
        st.dataframe(df_filtrado)
