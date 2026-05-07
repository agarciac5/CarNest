from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from inventario.models import Vehiculo
from .models import Venta


def _get_carrito(request):
    return request.session.get('carrito', [])


def _save_carrito(request, lista):
    request.session['carrito'] = lista
    request.session.modified = True


@login_required
def ver_carrito(request):
    pks = _get_carrito(request)
    vehiculos = Vehiculo.objects.filter(pk__in=pks)

    pks_validos = [v.pk for v in vehiculos if v.estado == 'en_venta']
    pks_removidos = [pk for pk in pks if pk not in pks_validos]

    if pks_removidos:
        _save_carrito(request, pks_validos)
        messages.warning(
            request,
            _('%(n)d vehículo(s) fueron removidos porque ya no están disponibles.') % {'n': len(pks_removidos)}
        )
        vehiculos = vehiculos.filter(estado='en_venta')

    total = sum(v.precio for v in vehiculos)

    return render(request, 'ventas/carrito.html', {
        'vehiculos': vehiculos,
        'total': total,
        'carrito_vacio': not pks_validos,
    })


@login_required
def agregar_al_carrito(request, pk):
    if request.method != 'POST':
        return redirect('lista_vehiculos')

    vehiculo = get_object_or_404(Vehiculo, pk=pk, estado='en_venta')
    carrito = _get_carrito(request)

    if vehiculo.pk in carrito:
        messages.info(request, _('%(v)s ya está en tu carrito.') % {'v': str(vehiculo)})
    else:
        carrito.append(vehiculo.pk)
        _save_carrito(request, carrito)
        messages.success(request, _('%(v)s añadido al carrito.') % {'v': str(vehiculo)})

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'lista_vehiculos'
    return redirect(next_url)


@login_required
def eliminar_del_carrito(request, pk):
    if request.method != 'POST':
        return redirect('ver_carrito')

    carrito = _get_carrito(request)
    if pk in carrito:
        carrito.remove(pk)
        _save_carrito(request, carrito)
        messages.success(request, _('Vehículo eliminado del carrito.'))

    return redirect('ver_carrito')


@login_required
def confirmar_compra(request):
    if request.method != 'POST':
        return redirect('ver_carrito')

    pks = _get_carrito(request)
    if not pks:
        messages.warning(request, _('Tu carrito está vacío.'))
        return redirect('ver_carrito')

    vehiculos = Vehiculo.objects.filter(pk__in=pks, estado='en_venta')
    if not vehiculos.exists():
        messages.error(request, _('Ningún vehículo disponible para comprar.'))
        _save_carrito(request, [])
        return redirect('ver_carrito')

    comprados = []
    errores = []

    for vehiculo in vehiculos:
        venta = Venta(
            vehiculo=vehiculo,
            comprador=request.user,
            precio_final=vehiculo.precio,
        )
        try:
            venta.realizar_venta()
            comprados.append(str(vehiculo))
        except ValidationError as e:
            errores.append(f'{vehiculo}: {e.message}')

    _save_carrito(request, [])

    if comprados:
        messages.success(request, _('¡Compra exitosa! Adquiriste: %(v)s.') % {'v': ', '.join(comprados)})
    if errores:
        messages.error(request, _('No se pudieron comprar: %(e)s') % {'e': '; '.join(errores)})

    return redirect('mis_compras')


@login_required
def mis_compras(request):
    compras = (
        Venta.objects
        .filter(comprador=request.user)
        .select_related('vehiculo')
        .order_by('-fecha')
    )
    return render(request, 'ventas/mis_compras.html', {'compras': compras})