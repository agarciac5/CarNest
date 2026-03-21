from django.shortcuts import render, redirect, get_object_or_404
from inventario.models import Vehiculo
from django.contrib.auth.decorators import login_required

@login_required
def lista_anuncios(request):

    if not request.user.is_staff:
        return redirect('/') 

    vehiculos = Vehiculo.objects.filter(estado='posteado')

    return render(request, 'anuncios/anuncios.html', {
        'vehiculos': vehiculos
    })


@login_required
def comprar_vehiculo(request, id):

    if not request.user.is_staff:
        return redirect('/')

    vehiculo = get_object_or_404(Vehiculo, id=id)
    vehiculo.comprar_por_admin()

    return redirect('/anuncios/')