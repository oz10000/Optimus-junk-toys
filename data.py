# data.py - REESCRITO (clonado de data_engine.py de junktoys)
import os
import time
import pandas as pd
import ccxt
from typing import Optional, List
from config import CONFIG

class DataProvider:
    EXCHANGE_PRIORITY = ['binance', 'okx', 'kucoin', 'mexc', 'kraken', 'bybit']

    def __init__(self, exchanges: Optional[List[str]] = None):
        if exchanges is None:
            exchanges = self.EXCHANGE_PRIORITY
        self.exchanges = {}
        self.primary = None
        self.cache_dir = CONFIG.cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

        for ex_id in exchanges:
            try:
                ex = getattr(ccxt, ex_id)({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})
                ex.load_markets()
                self.exchanges[ex_id] = ex
                if self.primary is None:
                    self.primary = ex_id
            except Exception as e:
                print(f"⚠️ No se pudo conectar a {ex_id}: {e}")

        if not self.exchanges:
            raise RuntimeError("No hay exchanges disponibles")

    def get_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 500,
                  use_cache: bool = True) -> Optional[pd.DataFrame]:
        cache_file = os.path.join(self.cache_dir, f"{symbol.replace('/', '_')}_{timeframe}_{limit}.parquet")
        if use_cache and os.path.exists(cache_file):
            try:
                df = pd.read_parquet(cache_file)
                if (pd.Timestamp.now() - df.index[-1]).total_seconds() < 3600:
                    return df
            except Exception:
                pass

        for ex_id, exchange in self.exchanges.items():
            for attempt in range(3):
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                    if not ohlcv:
                        continue
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    if use_cache:
                        try:
                            df.to_parquet(cache_file)
                        except Exception:
                            pass
                    return df
                except ccxt.RateLimitExceeded:
                    time.sleep((attempt + 1) * 2)
                except ccxt.BadSymbol:
                    break
                except Exception as e:
                    print(f"❌ Error en {ex_id}: {e}")
                    time.sleep(1)
        return None

    def get_certified_assets(self, symbols: Optional[List[str]] = None) -> List[str]:
        if symbols is None:
            symbols = CONFIG.universe
        exchange = self.exchanges.get(self.primary)
        if exchange is None:
            return []
        markets = exchange.load_markets()
        return [s for s in symbols if s in markets]
