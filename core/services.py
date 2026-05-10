"""
core/services.py
----------------
Punto 8 - Consumo de API externa de terceros.
Punto 3 - Inversión de dependencias: UNA interfaz, DOS clases concretas.

Clases:
    TipoCambioService      → obtiene tasa en vivo desde open.er-api.com
    TipoCambioFijoService  → usa tasa fija hardcodeada (fallback sin red)

Ambas implementan ITipoCambioService (definido en core/protocols.py).
El inyector en core/dependencies.py decide cuál usar:
    - Intenta TipoCambioService (API en vivo)
    - Si falla, cae automáticamente a TipoCambioFijoService
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

# Tasa fija de respaldo (COP por 1 USD) — se actualiza manualmente si es necesario
_TASA_FIJA_COP = 4200.0


# ═══════════════════════════════════════════════════════════════════
# Clase concreta 1: TipoCambioService (API en vivo)
# ═══════════════════════════════════════════════════════════════════

class TipoCambioService:
    """
    Implementación concreta 1 de ITipoCambioService.
    Obtiene la tasa USD→COP en tiempo real desde open.er-api.com.
    Cachea el resultado 10 minutos para no saturar la API.
    """

    def __init__(self, api_url: str = _API_URL, cache_ttl: int = _CACHE_TTL):
        self._api_url = api_url
        self._cache_ttl = cache_ttl
        self._tasa_cache: Optional[float] = None
        self._cache_timestamp: float = 0.0

    def cop_a_usd(self, monto_cop: float) -> Optional[float]:
        """Convierte COP a USD. Retorna None si la API no está disponible."""
        tasa = self._obtener_tasa_usd_a_cop()
        if tasa is None or tasa == 0:
            return None
        return round(float(monto_cop) / tasa, 2)

    def obtener_tasa_usd_cop(self) -> Optional[float]:
        """Devuelve cuántos COP vale 1 USD. None si falla la API."""
        return self._obtener_tasa_usd_a_cop()

    def _obtener_tasa_usd_a_cop(self) -> Optional[float]:
        ahora = time.time()
        if self._tasa_cache and (ahora - self._cache_timestamp) < self._cache_ttl:
            return self._tasa_cache
        tasa = self._fetch_tasa()
        if tasa:
            self._tasa_cache = tasa
            self._cache_timestamp = ahora
        return tasa

    def _fetch_tasa(self) -> Optional[float]:
        try:
            req = urllib.request.Request(
                self._api_url,
                headers={
                    'Accept': 'application/json',
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


# ═══════════════════════════════════════════════════════════════════
# Clase concreta 2: TipoCambioFijoService (fallback sin red)
# ═══════════════════════════════════════════════════════════════════

class TipoCambioFijoService:
    """
    Implementación concreta 2 de ITipoCambioService.
    Usa una tasa fija hardcodeada — no requiere red ni API key.
    Se usa como fallback cuando TipoCambioService no puede conectarse.

    Ventajas:
        - Siempre disponible (offline, tests, entornos sin internet)
        - Respuesta instantánea sin latencia de red
    Desventajas:
        - Tasa desactualizada (hay que actualizarla manualmente)
    """

    def __init__(self, tasa_cop: float = _TASA_FIJA_COP):
        self._tasa_cop = tasa_cop
        logger.info('TipoCambioFijoService activo: 1 USD = %.2f COP (tasa fija)', tasa_cop)

    def cop_a_usd(self, monto_cop: float) -> Optional[float]:
        """Convierte COP a USD usando tasa fija. Siempre retorna un valor."""
        if self._tasa_cop == 0:
            return None
        return round(float(monto_cop) / self._tasa_cop, 2)

    def obtener_tasa_usd_cop(self) -> Optional[float]:
        """Devuelve la tasa fija configurada."""
        return self._tasa_cop


# ═══════════════════════════════════════════════════════════════════
# TipoCambioConFallback: orquesta las dos clases anteriores
# ═══════════════════════════════════════════════════════════════════

class TipoCambioConFallback:
    """
    Combina TipoCambioService y TipoCambioFijoService.
    Intenta primero la API en vivo; si falla, usa la tasa fija.
    Este es el servicio que se usa en producción.
    """

    def __init__(
        self,
        servicio_vivo: Optional[TipoCambioService] = None,
        servicio_fijo: Optional[TipoCambioFijoService] = None,
    ):
        self._vivo = servicio_vivo or TipoCambioService()
        self._fijo = servicio_fijo or TipoCambioFijoService()

    def cop_a_usd(self, monto_cop: float) -> Optional[float]:
        resultado = self._vivo.cop_a_usd(monto_cop)
        if resultado is None:
            logger.info('TipoCambio: API falló, usando tasa fija como fallback')
            resultado = self._fijo.cop_a_usd(monto_cop)
        return resultado

    def obtener_tasa_usd_cop(self) -> Optional[float]:
        tasa = self._vivo.obtener_tasa_usd_cop()
        if tasa is None:
            logger.info('TipoCambio: API falló, usando tasa fija como fallback')
            tasa = self._fijo.obtener_tasa_usd_cop()
        return tasa