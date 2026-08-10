# data.py (Optimus-junk-toys) - VERSIÓN MEJORADA CON REINTENTOS Y FAILOVER
import os
import time
import pandas as pd
import ccxt
from typing import Optional
from config import CONFIG

class DataProvider:
    def __init__(self, exchange_ids: list = None):
        if exchange_ids is None:
            exchange_ids = ['binance', 'okx', 'kucoin', 'mexc']
        self.exchanges = {}
        self.primary = None
        for ex_id in exchange_ids:
            try:
                ex = getattr(ccxt, ex_id)({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
                ex.load_markets()
                self.exchanges[ex_id] = ex
                if self.primary is None:
                    self.primary = ex_id
                print(f"✅ Conectado a {ex_id}")
            except Exception as e:
                print(f"⚠️ No se pudo conectar a {ex_id}: {e}")

        self.cache_dir = CONFIG.cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 500, 
                  use_cache: bool = True) -> Optional[pd.DataFrame]:
        # 1. Intentar cargar desde caché
        cache_file = os.path.join(
            self.cache_dir,
            f"{symbol.replace('/', '_')}_{timeframe}_{limit}.parquet"
        )
        if use_cache and os.path.exists(cache_file):
            try:
                df = pd.read_parquet(cache_file)
                if (pd.Timestamp.now() - df.index[-1]).total_seconds() < 3600:
                    return df
            except Exception:
                pass

        # 2. Intentar descargar con reintentos y failover
        for ex_id, exchange in self.exchanges.items():
            for attempt in range(3):
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                    if ohlcv:
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
                    wait = (attempt + 1) * 2
                    print(f"⏳ Rate limit en {ex_id}. Esperando {wait}s...")
                    time.sleep(wait)
                except ccxt.BadSymbol:
                    print(f"❌ Símbolo {symbol} no existe en {ex_id}")
                    break  # Probar con otro exchange
                except Exception as e:
                    print(f"❌ Error en {ex_id} (intento {attempt+1}/3): {e}")
                    time.sleep(1)
            # Si llegamos aquí, este exchange falló, probar el siguiente

        print(f"❌ No se pudo descargar {symbol} después de todos los intentos")
        return None
