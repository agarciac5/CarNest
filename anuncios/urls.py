from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_anuncios, name='anuncios'),
    path('comprar/<int:id>/', views.comprar_vehiculo, name='comprar_vehiculo'),
]