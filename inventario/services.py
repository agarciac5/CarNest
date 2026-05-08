from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Vehiculo


def listar_vehiculos_posteados(q=''):
    vehiculos = Vehiculo.objects.filter(estado='posteado').select_related('propietario')
    if q:
        vehiculos = vehiculos.filter(
            Q(marca__icontains=q)
            | Q(modelo__icontains=q)
            | Q(propietario__username__icontains=q)
        )
    return vehiculos


@transaction.atomic
def aprobar_vehiculo_posteado(vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, estado='posteado')
    vehiculo.comprar_por_admin()
    return vehiculo


@transaction.atomic
def rechazar_vehiculo_posteado(vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, estado='posteado')
    nombre = str(vehiculo)
    vehiculo.delete()
    return nombre
