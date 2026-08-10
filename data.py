# data.py
import os
import time
import logging
import pandas as pd
import ccxt
from typing import Optional, List
from config import CONFIG

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProvider:
    """
    Proveedor de datos con múltiples exchanges, reintentos y caché.
    Clonado del data_engine.py de junktoys.
    """

    # Orden de prioridad de exchanges (el primero disponible será el primario)
    EXCHANGE_PRIORITY = ['binance', 'okx', 'kucoin', 'mexc', 'kraken', 'bybit']

    def __init__(self, exchanges: Optional[List[str]] = None):
        """
        Inicializa el proveedor conectando a los exchanges disponibles.
        """
        if exchanges is None:
            exchanges = self.EXCHANGE_PRIORITY

        self.exchanges = {}
        self.primary = None
        self.cache_dir = CONFIG.cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

        for ex_id in exchanges:
            try:
                ex_class = getattr(ccxt, ex_id)
                exchange = ex_class({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'},
                    'rateLimit': 1200,
                })
                # Cargar mercados para verificar conectividad
                exchange.load_markets()
                self.exchanges[ex_id] = exchange
                if self.primary is None:
                    self.primary = ex_id
                logger.info(f"✅ Conectado a {ex_id}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo conectar a {ex_id}: {e}")

        if not self.exchanges:
            logger.error("❌ No se pudo conectar a ningún exchange")
            raise RuntimeError("No hay exchanges disponibles")

        logger.info(f"📡 Exchange primario: {self.primary}")

    def get_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 500,
                  use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Obtiene velas OHLCV con caché, reintentos y failover entre exchanges.
        """
        # 1. Intentar cargar desde caché
        cache_file = os.path.join(
            self.cache_dir,
            f"{symbol.replace('/', '_')}_{timeframe}_{limit}.parquet"
        )

        if use_cache and os.path.exists(cache_file):
            try:
                df = pd.read_parquet(cache_file)
                # Validar que los datos no estén obsoletos (más de 1 hora)
                if (pd.Timestamp.now() - df.index[-1]).total_seconds() < 3600:
                    logger.debug(f"✅ Caché válido para {symbol}")
                    return df
                else:
                    logger.debug(f"⏳ Caché obsoleto para {symbol}, descargando...")
            except Exception as e:
                logger.warning(f"⚠️ Error leyendo caché de {symbol}: {e}")

        # 2. Intentar descargar con cada exchange
        for ex_id, exchange in self.exchanges.items():
            for attempt in range(3):  # 3 intentos por exchange
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                    if not ohlcv:
                        logger.warning(f"⚠️ No se obtuvieron velas para {symbol} desde {ex_id}")
                        continue

                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    df.sort_index(inplace=True)

                    # Guardar en caché
                    if use_cache:
                        try:
                            df.to_parquet(cache_file)
                            logger.debug(f"💾 Caché guardado para {symbol}")
                        except Exception as e:
                            logger.warning(f"⚠️ No se pudo guardar caché de {symbol}: {e}")

                    logger.info(f"✅ Descargado {symbol} desde {ex_id} ({len(df)} velas)")
                    return df

                except ccxt.RateLimitExceeded:
                    wait = (attempt + 1) * 2  # 2, 4, 6 segundos
                    logger.warning(f"⏳ Rate limit en {ex_id} (intento {attempt+1}/3). Esperando {wait}s...")
                    time.sleep(wait)

                except ccxt.BadSymbol:
                    logger.warning(f"❌ Símbolo {symbol} no existe en {ex_id}")
                    break  # Probar con otro exchange

                except Exception as e:
                    logger.error(f"❌ Error en {ex_id} (intento {attempt+1}/3): {e}")
                    time.sleep(1)

            # Si llegamos aquí, este exchange falló, probar el siguiente
            logger.warning(f"⚠️ {ex_id} falló para {symbol}, probando siguiente exchange...")

        # 3. Si todos los exchanges fallan, retornar None
        logger.error(f"❌ No se pudo descargar {symbol} después de todos los intentos")
        return None

    def get_certified_assets(self, symbols: Optional[List[str]] = None) -> List[str]:
        """
        Verifica qué símbolos existen en el exchange primario y retorna los válidos.
        """
        if symbols is None:
            symbols = CONFIG.universe

        certified = []
        exchange = self.exchanges.get(self.primary)
        if exchange is None:
            logger.error("❌ No hay exchange primario disponible para certificar activos")
            return certified

        markets = exchange.load_markets()
        for sym in symbols:
            # Normalizar símbolo: si es 'BTC/USDT' lo dejamos, si es 'BTCUSDT' lo formateamos
            if '/' not in sym:
                sym = f"{sym}/USDT"
            if sym in markets:
                certified.append(sym)
                logger.debug(f"✅ Activo certificado: {sym}")
            else:
                logger.warning(f"⚠️ Activo no encontrado: {sym}")

        return certified

    def get_available_timeframes(self, exchange_id: Optional[str] = None) -> List[str]:
        """
        Retorna los timeframes disponibles en el exchange.
        """
        if exchange_id is None:
            exchange_id = self.primary
        exchange = self.exchanges.get(exchange_id)
        if exchange is None:
            return ['1m', '5m', '15m', '1h', '4h', '1d']
        return list(exchange.timeframes.keys()) if hasattr(exchange, 'timeframes') else []
