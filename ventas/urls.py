from django.urls import path

from inventario import views


urlpatterns = [
    path('comprar/<int:id>/', views.comprar_cliente, name='comprar_cliente'),
]