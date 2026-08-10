import pandas as pd
import os
import streamlit as st   # <-- Agregado

class DataLoader:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), 'data', 'dataset.csv')
    
    def load_data(self):
        try:
            return pd.read_csv(self.data_path)
        except FileNotFoundError:
            st.error("Archivo de datos no encontrado. Asegúrate de que dataset.csv esté en data/")
            return pd.DataFrame()
