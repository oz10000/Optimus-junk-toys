# data.py
import ccxt
import pandas as pd
import numpy as np
import pickle
import hashlib
import os
from typing import Optional, Dict, List
from config import CONFIG

class DataProvider:
    """Proveedor de datos OHLCV con caché y checksum."""

    def __init__(self, exchange_id: str = 'binance'):
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.cache_dir = CONFIG.cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self._memory_cache: Dict[str, pd.DataFrame] = {}

    def get_ohlcv(self, symbol: str, timeframe: str = None, limit: int = 300,
                  force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """Obtiene velas OHLCV con caché."""
        timeframe = timeframe or CONFIG.timeframe
        cache_key = hashlib.md5(f"{symbol}_{timeframe}_{limit}".encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        meta_path = os.path.join(self.cache_dir, f"{cache_key}.meta")

        if not force_refresh and cache_key in self._memory_cache:
            return self._memory_cache[cache_key]

        if not force_refresh and os.path.exists(cache_path) and os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    stored_hash = f.read().strip()
                with open(cache_path, 'rb') as f:
                    df = pickle.load(f)
                current_hash = hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()
                if current_hash == stored_hash:
                    self._memory_cache[cache_key] = df
                    return df
            except:
                pass

        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                return None
            df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df.astype(float)

            checksum = hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()
            with open(cache_path, 'wb') as f:
                pickle.dump(df, f)
            with open(meta_path, 'w') as f:
                f.write(checksum)

            self._memory_cache[cache_key] = df
            return df

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

    def get_multi_timeframe(self, symbol: str, timeframes: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Obtiene velas para múltiples timeframes."""
        if timeframes is None:
            timeframes = list(CONFIG.mtf_weights.keys())
        result = {}
        for tf in timeframes:
            if CONFIG.mtf_weights.get(tf, 0) > 0:
                df = self.get_ohlcv(symbol, timeframe=tf, limit=100)
                if df is not None:
                    result[tf] = df
        return result
