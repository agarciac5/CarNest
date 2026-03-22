from django.urls import path
from .views import lista_vehiculos, crear_vehiculo, detalle_vehiculo

urlpatterns = [
    path('', lista_vehiculos, name='lista_vehiculos'),
    path('crear/', crear_vehiculo, name='crear_vehiculo'),
    path('<int:pk>/', detalle_vehiculo, name='detalle_vehiculo'),
]
