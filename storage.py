# storage.py
import json
import pickle
import pandas as pd
from datetime import datetime
import os
from config import CONFIG

class Storage:
    """Persistencia de datos, trades y métricas."""

    def __init__(self):
        os.makedirs(CONFIG.results_dir, exist_ok=True)
        os.makedirs(CONFIG.logs_dir, exist_ok=True)

    def save_trades(self, trades: list, filename: str = None):
        if filename is None:
            filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(CONFIG.results_dir, filename)
        with open(path, 'w') as f:
            json.dump(trades, f, indent=2, default=str)

    def load_trades(self, filename: str) -> list:
        path = os.path.join(CONFIG.results_dir, filename)
        with open(path, 'r') as f:
            return json.load(f)

    def save_metrics(self, metrics: dict, filename: str = None):
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(CONFIG.results_dir, filename)
        with open(path, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)

    def log(self, message: str, level: str = 'INFO'):
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)
        log_path = os.path.join(CONFIG.logs_dir, f"log_{datetime.now().strftime('%Y%m%d')}.txt")
        with open(log_path, 'a') as f:
            f.write(log_line + '\n')
