from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .services import aprobar_anuncio, listar_anuncios_pendientes, rechazar_anuncio


@login_required
def lista_anuncios(request):
    if request.user.rol != request.user.Rol.ADMIN:
        return redirect('/')

    q = (request.GET.get('q') or '').strip()
    vehiculos = listar_anuncios_pendientes(q)

    return render(request, 'anuncios/anuncios.html', {
        'vehiculos': vehiculos,
        'q': q,
    })


@login_required
def comprar_vehiculo(request, id):
    if request.user.rol != request.user.Rol.ADMIN:
        return redirect('/')
    if request.method != 'POST':
        return redirect('anuncios')

    vehiculo = aprobar_anuncio(id, request.user)

    messages.success(request, _('%(v)s fue comprado y ya aparece en el inventario.') % {'v': str(vehiculo)})
    return redirect('anuncios')


@login_required
def rechazar_vehiculo(request, id):
    if request.user.rol != request.user.Rol.ADMIN:
        return redirect('/')
    if request.method != 'POST':
        return redirect('anuncios')

    nombre = rechazar_anuncio(id)

    messages.warning(request, _('El anuncio de "%(v)s" fue rechazado y eliminado.') % {'v': nombre})
    return redirect('anuncios')
