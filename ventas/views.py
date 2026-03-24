from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from inventario.models import Vehiculo
from .models import Venta


# ── Helpers de sesión ──────────────────────────────────────────────

def _get_carrito(request):
    """Devuelve la lista de PKs en el carrito (guardada en sesión)."""
    return request.session.get('carrito', [])


def _save_carrito(request, lista):
    """Persiste la lista de PKs en la sesión y fuerza guardado."""
    request.session['carrito'] = lista
    request.session.modified = True


# ── Vistas ─────────────────────────────────────────────────────────

@login_required
def ver_carrito(request):
    """
    Muestra los vehículos en el carrito.
    Si algún vehículo ya fue vendido, lo elimina automáticamente y avisa.
    """
    pks = _get_carrito(request)
    vehiculos = Vehiculo.objects.filter(pk__in=pks)

    # Limpiar del carrito vehículos que ya no están en_venta
    pks_validos = [v.pk for v in vehiculos if v.estado == 'en_venta']
    pks_removidos = [pk for pk in pks if pk not in pks_validos]

    if pks_removidos:
        _save_carrito(request, pks_validos)
        messages.warning(
            request,
            f"{len(pks_removidos)} vehículo(s) fueron removidos porque ya no están disponibles."
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
    """
    Agrega un vehículo al carrito por su PK.
    - Solo acepta POST (protección CSRF).
    - No permite duplicados.
    - Solo vehículos con estado 'en_venta'.
    """
    if request.method != 'POST':
        return redirect('lista_vehiculos')

    vehiculo = get_object_or_404(Vehiculo, pk=pk, estado='en_venta')
    carrito = _get_carrito(request)

    if vehiculo.pk in carrito:
        messages.info(request, f'"{vehiculo}" ya está en tu carrito.')
    else:
        carrito.append(vehiculo.pk)
        _save_carrito(request, carrito)
        messages.success(request, f'"{vehiculo}" añadido al carrito.')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'lista_vehiculos'
    return redirect(next_url)


@login_required
def eliminar_del_carrito(request, pk):
    """Elimina un vehículo del carrito por su PK."""
    if request.method != 'POST':
        return redirect('ver_carrito')

    carrito = _get_carrito(request)
    if pk in carrito:
        carrito.remove(pk)
        _save_carrito(request, carrito)
        messages.success(request, 'Vehículo eliminado del carrito.')

    return redirect('ver_carrito')


@login_required
def confirmar_compra(request):
    """
    Procesa la compra de todos los vehículos en el carrito.
    - Solo POST.
    - Crea un objeto Venta por cada vehículo.
    - Llama a venta.realizar_venta() que cambia estado a 'vendido'.
    - Vacía el carrito al finalizar.
    """
    if request.method != 'POST':
        return redirect('ver_carrito')

    pks = _get_carrito(request)
    if not pks:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')

    vehiculos = Vehiculo.objects.filter(pk__in=pks, estado='en_venta')
    if not vehiculos.exists():
        messages.error(request, 'Ningún vehículo disponible para comprar.')
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
        messages.success(
            request,
            f'¡Compra exitosa! Adquiriste: {", ".join(comprados)}.'
        )
    if errores:
        messages.error(
            request,
            f'No se pudieron comprar: {"; ".join(errores)}'
        )

    return redirect('mis_compras')


@login_required
def mis_compras(request):
    """Historial de compras del usuario autenticado."""
    compras = (
        Venta.objects
        .filter(comprador=request.user)
        .select_related('vehiculo')
        .order_by('-fecha')
    )
    return render(request, 'ventas/mis_compras.html', {'compras': compras})