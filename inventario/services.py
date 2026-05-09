from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import FotoVehiculo, Vehiculo


def listar_vehiculos_en_venta(q=''):
    vehiculos = Vehiculo.objects.filter(estado='en_venta').select_related('propietario')
    if q:
        filtro = (
            Q(marca__icontains=q)
            | Q(modelo__icontains=q)
            | Q(color__icontains=q)
            | Q(descripcion__icontains=q)
        )
        if q.isdigit():
            filtro |= Q(año=int(q))
        vehiculos = vehiculos.filter(filtro)
    return vehiculos


def obtener_detalle_vehiculo_en_venta(pk):
    return get_object_or_404(
        Vehiculo.objects.filter(estado='en_venta').select_related('propietario'),
        pk=pk,
    )


def obtener_navegacion_vehiculo(vehiculo, q=''):
    vehiculos = listar_vehiculos_en_venta(q)
    ids = list(vehiculos.values_list('pk', flat=True))
    prev_id = next_id = None
    if ids:
        try:
            i = ids.index(vehiculo.pk)
            if i > 0:
                prev_id = ids[i - 1]
            if i < len(ids) - 1:
                next_id = ids[i + 1]
        except ValueError:
            pass
    return prev_id, next_id


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
def crear_vehiculo_desde_form(data, files, propietario):
    vehiculo = Vehiculo.objects.create(
        marca=data['marca'].strip(),
        modelo=data['modelo'].strip(),
        año=int(data['año']),
        precio=data['precio'],
        kilometraje=int(data.get('kilometraje') or 0),
        color=data.get('color', '').strip(),
        combustible=data.get('combustible', 'gasolina'),
        transmision=data.get('transmision', 'manual'),
        descripcion=data.get('descripcion', '').strip(),
        propietario=propietario,
        estado='en_venta',
    )
    if files.get('imagen'):
        vehiculo.imagen = files['imagen']
        vehiculo.save()
    for orden, foto in enumerate(files.getlist('fotos_extra')):
        if foto:
            FotoVehiculo.objects.create(vehiculo=vehiculo, imagen=foto, orden=orden)
    return vehiculo


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
