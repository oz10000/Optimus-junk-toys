# data.py
import os
import pandas as pd
import ccxt
from typing import Optional
from config import CONFIG

class DataProvider:
    """
    Proveedor de datos de mercado usando CCXT (Binance).
    Utiliza caché para evitar descargas repetidas.
    """

    def __init__(self, exchange_id: str = 'binance'):
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        # Asegurar que el directorio de caché existe
        self.cache_dir = CONFIG.cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def get_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 1000,
                  use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Descarga velas OHLCV desde Binance, con caché opcional.
        Retorna un DataFrame con índice datetime.
        """
        # Construir nombre de archivo de caché
        cache_file = os.path.join(
            self.cache_dir,
            f"{symbol.replace('/', '_')}_{timeframe}_{limit}.parquet"
        )

        # Intentar cargar desde caché
        if use_cache and os.path.exists(cache_file):
            try:
                df = pd.read_parquet(cache_file)
                # Verificar que los datos no estén obsoletos (última vela de hoy)
                last_time = df.index[-1]
                if (pd.Timestamp.now() - last_time).total_seconds() < 3600:  # 1 hora
                    return df
            except Exception:
                pass  # Si falla la carga, descargar de nuevo

        # Descargar desde el exchange
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Guardar en caché
            if use_cache:
                try:
                    df.to_parquet(cache_file)
                except Exception:
                    pass  # Si falla el guardado, continuar sin caché

            return df
        except Exception as e:
            print(f"❌ Error fetching {symbol} {timeframe}: {e}")
            return None
