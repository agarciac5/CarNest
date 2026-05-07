from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from core.views import home

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
] + i18n_patterns(
    path('', home, name='home'),  # ← name='home' añadido
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('inventario/', include('inventario.urls')),
    path('anuncios/', include('anuncios.urls')),
    path('', include('ventas.urls')),
    prefix_default_language=False,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)