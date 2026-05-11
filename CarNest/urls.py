from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from core.views import home
from core.api_views import (
    api_vehiculos,
    api_vehiculo_detalle,
    api_tipo_cambio,
    api_mis_compras,
)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/vehiculos/', api_vehiculos, name='api_vehiculos'),
    path('api/vehiculos/<int:pk>/', api_vehiculo_detalle, name='api_vehiculo_detalle'),
    path('api/tipo-cambio/', api_tipo_cambio, name='api_tipo_cambio'),
    path('api/mis-compras/', api_mis_compras, name='api_mis_compras'),
] + i18n_patterns(
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('inventario/', include('inventario.urls')),
    path('anuncios/', include('anuncios.urls')),
    path('', include('ventas.urls')),
    path('', home, name='home'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)