from django.urls import path
from .views import lista_vehiculos, crear_vehiculo, detalle_vehiculo, aviso_publicacion

urlpatterns = [
    path('', lista_vehiculos, name='lista_vehiculos'),
    path('crear/', crear_vehiculo, name='crear_vehiculo'),
    path('<int:pk>/', detalle_vehiculo, name='detalle_vehiculo'),
    path('publicado/', aviso_publicacion, name='aviso_publicacion'),  # ← NUEVO
]