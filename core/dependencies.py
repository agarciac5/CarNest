"""
core/dependencies.py
--------------------
Implementaciones concretas de los protocolos definidos en core/protocols.py.

Aquí se instancian los repositorios/servicios reales.
Las vistas y la API los obtienen llamando a get_*(),
lo que permite sustituir la implementación en tests
sin tocar una sola línea de vista.

Ejemplo en tests:
    from core import dependencies
    dependencies._vehiculo_repo = MiRepoFalso()
"""
from __future__ import annotations

from typing import Optional

# ── importaciones de servicios concretos ─────────────────────────────────────
from inventario.services import (
    listar_vehiculos_en_venta,
    obtener_detalle_vehiculo_en_venta,
    obtener_navegacion_vehiculo,
    crear_vehiculo_desde_form,
)
from anuncios.services import (
    listar_anuncios_pendientes,
    aprobar_anuncio,
    rechazar_anuncio,
)
from ventas.services import (
    obtener_vehiculos_carrito,
    obtener_vehiculo_en_venta,
    confirmar_compra_vehiculos,
    listar_compras_usuario,
)
from core.services import TipoCambioService


# ── wrappers que adaptan las funciones sueltas al protocolo de clase ──────────

class _VehiculoRepo:
    def listar_en_venta(self, q=''):
        return listar_vehiculos_en_venta(q)

    def obtener_detalle(self, pk):
        return obtener_detalle_vehiculo_en_venta(pk)

    def obtener_navegacion(self, vehiculo, q=''):
        return obtener_navegacion_vehiculo(vehiculo, q)

    def crear_desde_form(self, data, files, propietario):
        return crear_vehiculo_desde_form(data, files, propietario)


class _AnuncioRepo:
    def listar_pendientes(self, q=''):
        return listar_anuncios_pendientes(q)

    def aprobar(self, vehiculo_id, admin_user):
        return aprobar_anuncio(vehiculo_id, admin_user)

    def rechazar(self, vehiculo_id):
        return rechazar_anuncio(vehiculo_id)


class _VentaService:
    def obtener_vehiculos_carrito(self, pks):
        return obtener_vehiculos_carrito(pks)

    def obtener_vehiculo_en_venta(self, pk):
        return obtener_vehiculo_en_venta(pk)

    def confirmar_compra(self, pks, comprador):
        return confirmar_compra_vehiculos(pks, comprador)

    def listar_compras_usuario(self, usuario):
        return listar_compras_usuario(usuario)


# ── singletons (pueden reemplazarse en tests) ─────────────────────────────────
_vehiculo_repo: Optional[object] = None
_anuncio_repo: Optional[object] = None
_venta_service: Optional[object] = None
_tipo_cambio_service: Optional[object] = None


def get_vehiculo_repo():
    global _vehiculo_repo
    if _vehiculo_repo is None:
        _vehiculo_repo = _VehiculoRepo()
    return _vehiculo_repo


def get_anuncio_repo():
    global _anuncio_repo
    if _anuncio_repo is None:
        _anuncio_repo = _AnuncioRepo()
    return _anuncio_repo


def get_venta_service():
    global _venta_service
    if _venta_service is None:
        _venta_service = _VentaService()
    return _venta_service


def get_tipo_cambio_service():
    global _tipo_cambio_service
    if _tipo_cambio_service is None:
        _tipo_cambio_service = TipoCambioService()
    return _tipo_cambio_service