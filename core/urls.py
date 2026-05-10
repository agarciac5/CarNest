"""
core/urls.py
------------
URLs del módulo core: home + API JSON propia (Punto 6).
"""
from django.urls import path
from core.views import home
from core.api_views import (
    api_vehiculos,
    api_vehiculo_detalle,
    api_tipo_cambio,
    api_mis_compras,
)

urlpatterns = [
    # API JSON propia
    path('api/vehiculos/',        api_vehiculos,        name='api_vehiculos'),
    path('api/vehiculos/<int:pk>/', api_vehiculo_detalle, name='api_vehiculo_detalle'),
    path('api/tipo-cambio/',      api_tipo_cambio,      name='api_tipo_cambio'),
    path('api/mis-compras/',      api_mis_compras,      name='api_mis_compras'),
]