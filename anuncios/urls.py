from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_anuncios, name='anuncios'),
    path('comprar/<int:id>/', views.comprar_vehiculo, name='comprar_vehiculo'),
    path('rechazar/<int:id>/', views.rechazar_vehiculo, name='rechazar_vehiculo'),  # ← NUEVO
]