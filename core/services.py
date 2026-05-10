"""
core/services.py
----------------
Punto 8 - Consumo de API externa de terceros.
Punto 3 - Implementación concreta de ITipoCambioService.
 
Usa la API pública de open.er-api.com
que es gratuita, sin clave, y devuelve tipos de cambio reales.
 
Endpoint usado:
    GET https://open.er-api.com/v6/latest/USD
    → { "rates": { "COP": 4123.45, ... } }
 
El resultado se cachea en memoria por CACHE_TTL segundos
para no golpear la API en cada petición de página.
"""
from __future__ import annotations
 
import logging
import time
from typing import Optional
 
import urllib.request
import urllib.error
import json
 
logger = logging.getLogger(__name__)
 
# URL de la API externa (gratuita, sin API key)
_API_URL = 'https://open.er-api.com/v6/latest/USD'
 
# TTL del caché en memoria (10 minutos)
_CACHE_TTL = 600
 
 
class TipoCambioService:
    """
    Implementación concreta de ITipoCambioService.
    Obtiene la tasa USD→COP desde open.er-api.com y la cachea.
    """
 
    def __init__(self, api_url: str = _API_URL, cache_ttl: int = _CACHE_TTL):
        self._api_url = api_url
        self._cache_ttl = cache_ttl
        self._tasa_cache: Optional[float] = None
        self._cache_timestamp: float = 0.0
 
    # ── API pública ───────────────────────────────────────────────────────────
 
    def cop_a_usd(self, monto_cop: float) -> Optional[float]:
        """
        Convierte un monto en COP a USD.
        Retorna None si la API no está disponible.
        """
        tasa = self._obtener_tasa_usd_a_cop()
        if tasa is None or tasa == 0:
            return None
        return round(float(monto_cop) / tasa, 2)
 
    def obtener_tasa_usd_cop(self) -> Optional[float]:
        """Devuelve cuántos COP vale 1 USD. None si falla la API."""
        return self._obtener_tasa_usd_a_cop()
 
    # ── Lógica interna ────────────────────────────────────────────────────────
 
    def _obtener_tasa_usd_a_cop(self) -> Optional[float]:
        ahora = time.time()
 
        # Devolver caché si sigue vigente
        if self._tasa_cache and (ahora - self._cache_timestamp) < self._cache_ttl:
            return self._tasa_cache
 
        tasa = self._fetch_tasa()
        if tasa:
            self._tasa_cache = tasa
            self._cache_timestamp = ahora
 
        return tasa
 
    def _fetch_tasa(self) -> Optional[float]:
        """Llama a la API externa. Retorna la tasa o None ante cualquier error."""
        try:
            req = urllib.request.Request(
                self._api_url,
                headers={
                    'Accept': 'application/json',
                    # User-Agent de navegador para evitar bloqueos
                    'User-Agent': 'Mozilla/5.0 (compatible; CarNest/1.0)',
                },
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                tasa = data['rates']['COP']
                logger.info('TipoCambio actualizado: 1 USD = %.2f COP', tasa)
                return float(tasa)
        except urllib.error.URLError as e:
            logger.warning('TipoCambioService: error de red – %s', e)
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.warning('TipoCambioService: respuesta inesperada – %s', e)
        except Exception as e:
            logger.warning('TipoCambioService: error inesperado – %s', e)
        return None
 