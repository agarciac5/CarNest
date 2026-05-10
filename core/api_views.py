"""
core/api_views.py
-----------------
Punto 6 - Servicio web JSON propio.

Endpoints REST propios de CarNest que devuelven JSON.
No requieren autenticación para lectura (GET).
POST/acciones requieren login (decorador o sesión).

Endpoints:
    GET  /api/vehiculos/           → lista de vehículos en venta
    GET  /api/vehiculos/<pk>/      → detalle de un vehículo
    GET  /api/tipo-cambio/         → tasa USD↔COP actual
    GET  /api/mis-compras/         → compras del usuario autenticado
"""
from __future__ import annotations

import json
from decimal import Decimal

from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from core.dependencies import (
    get_vehiculo_repo,
    get_venta_service,
    get_tipo_cambio_service,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _vehiculo_a_dict(v) -> dict:
    """Serializa un Vehiculo a dict JSON-safe."""
    return {
        'id': v.pk,
        'marca': v.marca,
        'modelo': v.modelo,
        'año': v.año,
        'precio_cop': str(v.precio),
        'kilometraje': v.kilometraje,
        'color': v.color,
        'combustible': v.combustible,
        'combustible_display': v.get_combustible_display(),
        'transmision': v.transmision,
        'transmision_display': v.get_transmision_display(),
        'estado': v.estado,
        'fecha_publicacion': v.fecha_publicacion.isoformat(),
        'imagen_url': v.imagen.url if v.imagen else None,
        'url': v.get_absolute_url(),
    }


def _json_error(mensaje: str, status: int = 400) -> JsonResponse:
    return JsonResponse({'error': str(mensaje)}, status=status)


# ── Endpoint 1: lista de vehículos ────────────────────────────────────────────

@require_GET
def api_vehiculos(request):
    """
    GET /api/vehiculos/?q=toyota
    Devuelve la lista de vehículos en venta en JSON.
    Acepta parámetro opcional ?q= para filtrar.
    """
    q = (request.GET.get('q') or '').strip()
    repo = get_vehiculo_repo()
    vehiculos = repo.listar_en_venta(q)

    data = [_vehiculo_a_dict(v) for v in vehiculos]
    return JsonResponse({'count': len(data), 'results': data})


# ── Endpoint 2: detalle de un vehículo ───────────────────────────────────────

@require_GET
def api_vehiculo_detalle(request, pk):
    """
    GET /api/vehiculos/<pk>/
    Devuelve los datos completos de un vehículo en venta.
    Si no existe o no está en venta → 404.
    """
    repo = get_vehiculo_repo()
    tc_service = get_tipo_cambio_service()

    try:
        vehiculo = repo.obtener_detalle(pk)
    except Exception:
        return _json_error(_('Vehículo no encontrado.'), status=404)

    data = _vehiculo_a_dict(vehiculo)

    # Añadir precio en USD si la API externa responde
    precio_usd = tc_service.cop_a_usd(float(vehiculo.precio))
    data['precio_usd'] = precio_usd

    # Fotos extra
    data['fotos_extra'] = [
        f.imagen.url for f in vehiculo.fotos_extra.all()
    ]

    return JsonResponse(data)


# ── Endpoint 3: tipo de cambio ────────────────────────────────────────────────

@require_GET
def api_tipo_cambio(request):
    """
    GET /api/tipo-cambio/
    Devuelve la tasa de cambio actual USD↔COP.
    Ejemplo de respuesta:
        { "usd_a_cop": 4123.45, "fuente": "frankfurter.app" }
    """
    tc_service = get_tipo_cambio_service()
    tasa = tc_service.obtener_tasa_usd_cop()

    if tasa is None:
        return JsonResponse(
            {'usd_a_cop': None, 'fuente': 'frankfurter.app', 'disponible': False},
            status=503,
        )

    return JsonResponse({
        'usd_a_cop': tasa,
        'fuente': 'frankfurter.app',
        'disponible': True,
    })


# ── Endpoint 4: mis compras (requiere login) ──────────────────────────────────

@login_required
@require_GET
def api_mis_compras(request):
    """
    GET /api/mis-compras/
    Devuelve las compras del usuario autenticado en JSON.
    Requiere sesión activa (login).
    """
    venta_service = get_venta_service()
    compras = venta_service.listar_compras_usuario(request.user)

    data = [
        {
            'id': c.pk,
            'vehiculo': str(c.vehiculo),
            'vehiculo_id': c.vehiculo_id,
            'precio_final': str(c.precio_final),
            'fecha': c.fecha.isoformat(),
        }
        for c in compras
    ]
    return JsonResponse({'count': len(data), 'compras': data})