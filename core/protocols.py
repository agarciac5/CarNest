"""
core/protocols.py
-----------------
Inversión de dependencias (Punto 3).
 
Define los contratos (Protocolo) que las capas superiores (vistas, API)
deben recibir en lugar de importar servicios concretos directamente.
Esto permite sustituir implementaciones sin tocar las vistas.
 
Uso:
    from core.protocols import IVehiculoRepository, IVentaService
"""
from __future__ import annotations
 
from typing import Protocol, runtime_checkable, Iterable, Optional, Tuple, Any
 
 
@runtime_checkable
class IVehiculoRepository(Protocol):
    """Contrato para acceso a datos de Vehiculo."""
 
    def listar_en_venta(self, q: str = '') -> Iterable:
        ...
 
    def obtener_detalle(self, pk: int) -> Any:
        ...
 
    def obtener_navegacion(self, vehiculo: Any, q: str = '') -> Tuple[Optional[int], Optional[int]]:
        ...
 
    def crear_desde_form(self, data: dict, files: Any, propietario: Any) -> Any:
        ...
 
 
@runtime_checkable
class IAnuncioRepository(Protocol):
    """Contrato para anuncios pendientes de revisión."""
 
    def listar_pendientes(self, q: str = '') -> Iterable:
        ...
 
    def aprobar(self, vehiculo_id: int, admin_user: Any) -> Any:
        ...
 
    def rechazar(self, vehiculo_id: int) -> str:
        ...
 
 
@runtime_checkable
class IVentaService(Protocol):
    """Contrato para operaciones de venta y carrito."""
 
    def obtener_vehiculos_carrito(self, pks: list) -> Iterable:
        ...
 
    def obtener_vehiculo_en_venta(self, pk: int) -> Any:
        ...
 
    def confirmar_compra(self, pks: list, comprador: Any) -> Tuple[Iterable, list, list]:
        ...
 
    def listar_compras_usuario(self, usuario: Any) -> Iterable:
        ...
 
 
@runtime_checkable
class ITipoCambioService(Protocol):
    """Contrato para obtener tipos de cambio de divisas."""
 
    def cop_a_usd(self, monto_cop: float) -> Optional[float]:
        ...
 