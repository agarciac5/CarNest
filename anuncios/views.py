from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from inventario.models import Vehiculo
from ventas.models import Venta


@login_required
def lista_anuncios(request):
    if not request.user.is_staff:
        return redirect('/')

    q = (request.GET.get('q') or '').strip()
    vehiculos = Vehiculo.objects.filter(estado='posteado').select_related('propietario')
    if q:
        vehiculos = vehiculos.filter(
            marca__icontains=q
        ) | vehiculos.filter(
            modelo__icontains=q
        ) | vehiculos.filter(
            propietario__username__icontains=q
        )

    return render(request, 'anuncios/anuncios.html', {
        'vehiculos': vehiculos,
        'q': q,
    })


@login_required
def comprar_vehiculo(request, id):
    if not request.user.is_staff:
        return redirect('/')

    if request.method != 'POST':
        return redirect('anuncios')

    idioma = request.session.get('idioma', 'es')
    vehiculo = get_object_or_404(Vehiculo, id=id, estado='posteado')

    # Cambiar estado a en_venta
    vehiculo.comprar_por_admin()

    # Registrar en historial de compras del superuser
    Venta.objects.get_or_create(
        vehiculo=vehiculo,
        defaults={
            'comprador': request.user,
            'precio_final': vehiculo.precio,
        }
    )

    if idioma == 'en':
        messages.success(request, f'"{vehiculo}" was purchased and is now listed in the inventory.')
    else:
        messages.success(request, f'"{vehiculo}" fue comprado y ya aparece en el inventario.')

    return redirect('anuncios')


@login_required
def rechazar_vehiculo(request, id):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method != 'POST':
        return redirect('anuncios')

    idioma = request.session.get('idioma', 'es')
    vehiculo = get_object_or_404(Vehiculo, id=id, estado='posteado')
    nombre = str(vehiculo)
    vehiculo.delete()

    if idioma == 'en':
        messages.warning(request, f'The listing for "{nombre}" was rejected and removed.')
    else:
        messages.warning(request, f'El anuncio de "{nombre}" fue rechazado y eliminado.')

    return redirect('anuncios')