from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from inventario.models import Vehiculo
from .models import Venta


def obtener_vehiculos_carrito(pks):
    return Vehiculo.objects.filter(pk__in=pks)


def obtener_vehiculo_en_venta(pk):
    return get_object_or_404(Vehiculo, pk=pk, estado='en_venta')


@transaction.atomic
def vender_vehiculo(vehiculo, comprador):
    venta = Venta(
        vehiculo=vehiculo,
        comprador=comprador,
        precio_final=vehiculo.precio,
    )
    venta.realizar_venta()
    return venta


def confirmar_compra_vehiculos(pks, comprador):
    vehiculos = Vehiculo.objects.filter(pk__in=pks, estado='en_venta')
    comprados = []
    errores = []

    for vehiculo in vehiculos:
        try:
            vender_vehiculo(vehiculo, comprador)
            comprados.append(str(vehiculo))
        except ValidationError as e:
            errores.append(f'{vehiculo}: {e.message}')

    return vehiculos, comprados, errores


def listar_compras_usuario(usuario):
    return (
        Venta.objects
        .filter(comprador=usuario)
        .select_related('vehiculo')
        .order_by('-fecha')
    )
