from django.shortcuts import render, redirect
from .models import Vehiculo

from django.contrib.auth.decorators import login_required


def lista_vehiculos(request):
    vehiculos = vehiculos = Vehiculo.objects.filter(estado='en_venta')

    return render(request, 'inventario/inventary.html', {
        'vehiculos': vehiculos
    })
@login_required
def crear_vehiculo(request):
     
    if request.method == 'POST':
        Vehiculo.objects.create(
            marca=request.POST['marca'],
            modelo=request.POST['modelo'],
            año=request.POST['año'],
            precio=request.POST['precio'],
            propietario=request.user
        )
        return redirect('/inventario/')

    return render(request, 'inventario/crear_vehiculo.html')