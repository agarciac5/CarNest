from django.db import transaction

from inventario.services import (
    aprobar_vehiculo_posteado,
    listar_vehiculos_posteados,
    rechazar_vehiculo_posteado,
)
from ventas.models import Venta


def listar_anuncios_pendientes(q=''):
    return listar_vehiculos_posteados(q)


@transaction.atomic
def aprobar_anuncio(vehiculo_id, admin_user):
    vehiculo = aprobar_vehiculo_posteado(vehiculo_id)
    Venta.objects.get_or_create(
        vehiculo=vehiculo,
        defaults={
            'comprador': admin_user,
            'precio_final': vehiculo.precio,
        }
    )
    return vehiculo


def rechazar_anuncio(vehiculo_id):
    return rechazar_vehiculo_posteado(vehiculo_id)
