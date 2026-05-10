"""
inventario/views.py
-------------------
Punto 3 - Inversión de dependencias.
Punto 8 - Consumo API externa (precio en USD en detalle).

Las vistas ya no importan servicios concretos directamente.
Reciben sus dependencias a través de core.dependencies,
lo que permite sustituirlas en tests sin modificar este archivo.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from core.dependencies import get_vehiculo_repo, get_tipo_cambio_service


def lista_vehiculos(request):
    q = (request.GET.get('q') or '').strip()
    repo = get_vehiculo_repo()
    vehiculos = repo.listar_en_venta(q)
    return render(request, 'inventario/inventary.html', {
        'vehiculos': vehiculos,
        'q': q,
    })


def detalle_vehiculo(request, pk):
    q = (request.GET.get('q') or '').strip()
    repo = get_vehiculo_repo()
    tc_service = get_tipo_cambio_service()

    vehiculo = repo.obtener_detalle(pk)
    prev_id, next_id = repo.obtener_navegacion(vehiculo, q)

    # Punto 8: precio en USD usando API externa
    idioma = request.session.get('idioma', 'es')
    precio_usd = None
    if idioma == 'en':
        precio_usd = tc_service.cop_a_usd(float(vehiculo.precio))

    return render(request, 'inventario/detalle_vehiculo.html', {
        'vehiculo': vehiculo,
        'q': q,
        'prev_id': prev_id,
        'next_id': next_id,
        'precio_usd': precio_usd,
        'idioma': idioma,
    })


@login_required
def crear_vehiculo(request):
    if request.method == 'POST':
        repo = get_vehiculo_repo()
        vehiculo = repo.crear_desde_form(request.POST, request.FILES, request.user)
        return redirect('detalle_vehiculo', pk=vehiculo.pk)
    return render(request, 'inventario/crear_vehiculo.html')