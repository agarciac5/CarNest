from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .services import (
    crear_vehiculo_desde_form,
    listar_vehiculos_en_venta,
    obtener_detalle_vehiculo_en_venta,
    obtener_navegacion_vehiculo,
)


def lista_vehiculos(request):
    q = (request.GET.get('q') or '').strip()
    vehiculos = listar_vehiculos_en_venta(q)
    return render(request, 'inventario/inventary.html', {
        'vehiculos': vehiculos,
        'q': q,
    })


def detalle_vehiculo(request, pk):
    q = (request.GET.get('q') or '').strip()
    vehiculo = obtener_detalle_vehiculo_en_venta(pk)
    prev_id, next_id = obtener_navegacion_vehiculo(vehiculo, q)

    return render(request, 'inventario/detalle_vehiculo.html', {
        'vehiculo': vehiculo,
        'q': q,
        'prev_id': prev_id,
        'next_id': next_id,
    })


@login_required
def crear_vehiculo(request):
    if request.method == 'POST':
        vehiculo = crear_vehiculo_desde_form(request.POST, request.FILES, request.user)
        return redirect('detalle_vehiculo', pk=vehiculo.pk)

    return render(request, 'inventario/crear_vehiculo.html')
