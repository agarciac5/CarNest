from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import urllib.request
import json

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

    precio_usd = None
    if request.session.get('idioma') == 'en':
        try:
            url = 'https://open.er-api.com/v6/latest/COP'
            with urllib.request.urlopen(url, timeout=3) as resp:
                data = json.loads(resp.read())
            tasa = data['rates'].get('USD', None)
            if tasa:
                precio_usd = round(float(vehiculo.precio) * tasa, 2)
        except Exception:
            precio_usd = None

    return render(request, 'inventario/detalle_vehiculo.html', {
        'vehiculo': vehiculo,
        'q': q,
        'prev_id': prev_id,
        'next_id': next_id,
        'precio_usd': precio_usd,
    })


@login_required
def crear_vehiculo(request):
    if request.method == 'POST':

        # ── LÓGICA CLAVE: superuser → en_venta, usuario normal → posteado ──
        if request.user.is_superuser:
            estado_inicial = 'en_venta'
        else:
            estado_inicial = 'posteado'
        # ────────────────────────────────────────────────────────────────────

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
            estado=estado_inicial,
        )
        if request.FILES.get('imagen'):
            v.imagen = request.FILES['imagen']
            v.save()
        fotos = request.FILES.getlist('fotos_extra')
        for orden, f in enumerate(fotos):
            if f:
                FotoVehiculo.objects.create(vehiculo=v, imagen=f, orden=orden)

        # ── Redirigir según quién publicó ───────────────────────────────────
        if request.user.is_superuser:
            return redirect('detalle_vehiculo', pk=v.pk)  # va al inventario
        else:
            return redirect('aviso_publicacion')           # va a página de aviso
        # ────────────────────────────────────────────────────────────────────

    return render(request, 'inventario/crear_vehiculo.html')


def aviso_publicacion(request):
    """
    Página que se muestra al usuario normal tras publicar su vehículo.
    Le informa que su anuncio está pendiente de revisión por el equipo.
    """
    return render(request, 'inventario/aviso_publicacion.html')