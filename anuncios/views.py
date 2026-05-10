"""
anuncios/views.py
-----------------
Punto 3 - Inversión de dependencias.
Las vistas obtienen el repositorio de anuncios desde core.dependencies.
"""
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import gettext as _

from core.dependencies import get_anuncio_repo


@login_required
def lista_anuncios(request):
    if not request.user.is_staff:
        return redirect('lista_vehiculos')

    q = (request.GET.get('q') or '').strip()
    repo = get_anuncio_repo()
    vehiculos = repo.listar_pendientes(q)
    return render(request, 'anuncios/anuncios.html', {
        'vehiculos': vehiculos,
        'q': q,
    })


@login_required
def comprar_vehiculo(request, id):
    if request.method != 'POST' or not request.user.is_staff:
        return redirect('lista_vehiculos')

    repo = get_anuncio_repo()
    try:
        vehiculo = repo.aprobar(id, request.user)
        messages.success(request, _('Vehículo %(v)s aprobado y añadido al inventario.') % {'v': str(vehiculo)})
    except Exception as e:
        messages.error(request, str(e))

    return redirect('anuncios')


@login_required
def rechazar_vehiculo(request, id):
    if request.method != 'POST' or not request.user.is_staff:
        return redirect('lista_vehiculos')

    repo = get_anuncio_repo()
    try:
        nombre = repo.rechazar(id)
        messages.success(request, _('Anuncio "%(n)s" rechazado y eliminado.') % {'n': nombre})
    except Exception as e:
        messages.error(request, str(e))

    return redirect('anuncios')