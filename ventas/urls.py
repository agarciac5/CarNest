from django.urls import path
from . import views

urlpatterns = [
    path('carrito/',                   views.ver_carrito,          name='ver_carrito'),
    path('carrito/agregar/<int:pk>/',  views.agregar_al_carrito,   name='agregar_carrito'),
    path('carrito/eliminar/<int:pk>/', views.eliminar_del_carrito,  name='eliminar_carrito'),
    path('carrito/confirmar/',         views.confirmar_compra,      name='confirmar_compra'),
    path('mis-compras/',               views.mis_compras,           name='mis_compras'),
    path('comprar/<int:pk>/',          views.agregar_al_carrito,    name='comprar_cliente'),
]