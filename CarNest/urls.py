"""
CarNest/urls.py
---------------
URLconf principal. 
- Las rutas i18n_patterns llevan prefijo de idioma (/en/, sin prefijo para español).
- Las rutas de API van FUERA de i18n_patterns (no tienen prefijo de idioma)
  porque son consumidas por código, no por humanos.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from core.views import home

urlpatterns = [
    # Endpoint de Django para set_language (usado por i18n estándar)
    path('i18n/', include('django.conf.urls.i18n')),

    # ── API JSON propia — sin prefijo de idioma ───────────────────────
    path('', include('core.urls')),

] + i18n_patterns(
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('inventario/', include('inventario.urls')),
    path('anuncios/', include('anuncios.urls')),
    path('', include('ventas.urls')),
    prefix_default_language=False,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)