from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Vehiculo, FotoVehiculo


def _vehiculos_qs(request):
    q = (request.GET.get('q') or '').strip()
    qs = Vehiculo.objects.filter(estado='en_venta').select_related('propietario')
    if q:
        filtro = (
            Q(marca__icontains=q)
            | Q(modelo__icontains=q)
            | Q(color__icontains=q)
            | Q(descripcion__icontains=q)
        )
        if q.isdigit():
            filtro |= Q(año=int(q))
        qs = qs.filter(filtro)
    return qs, q


def lista_vehiculos(request):
    vehiculos, q = _vehiculos_qs(request)
    return render(request, 'inventario/inventary.html', {
        'vehiculos': vehiculos,
        'q': q,
    })


def detalle_vehiculo(request, pk):
    vehiculo = get_object_or_404(
        Vehiculo.objects.filter(estado='en_venta').select_related('propietario'),
        pk=pk,
    )
    vehiculos, q = _vehiculos_qs(request)
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

    return render(request, 'inventario/detalle_vehiculo.html', {
        'vehiculo': vehiculo,
        'q': q,
        'prev_id': prev_id,
        'next_id': next_id,
    })


@login_required
def crear_vehiculo(request):
    if request.method == 'POST':
        v = Vehiculo.objects.create(
            marca=request.POST['marca'].strip(),
            modelo=request.POST['modelo'].strip(),
            año=int(request.POST['año']),
            precio=request.POST['precio'],
            kilometraje=int(request.POST.get('kilometraje') or 0),
            color=request.POST.get('color', '').strip(),
            combustible=request.POST.get('combustible', 'gasolina'),
            transmision=request.POST.get('transmision', 'manual'),
            descripcion=request.POST.get('descripcion', '').strip(),
            propietario=request.user,
            estado='en_venta',
        )
        if request.FILES.get('imagen'):
            v.imagen = request.FILES['imagen']
            v.save()
        fotos = request.FILES.getlist('fotos_extra')
        for orden, f in enumerate(fotos):
            if f:
                FotoVehiculo.objects.create(vehiculo=v, imagen=f, orden=orden)
        return redirect('detalle_vehiculo', pk=v.pk)

    return render(request, 'inventario/crear_vehiculo.html')
