import os
from django.conf import settings


def carnest_branding(request):
    """
    Context processor global de CarNest.
    Inyecta el logo y el conteo del carrito en todos los templates.
    """
    logo_url = None
    logo_path_setting = getattr(settings, 'CARNEST_LOGO_PATH', '')

    if logo_path_setting:
        # Ruta explícita configurada en settings
        logo_url = settings.MEDIA_URL + logo_path_setting
    else:
        # Buscar automáticamente un archivo con 'gemini' en media/vehiculos/
        vehiculos_dir = os.path.join(settings.MEDIA_ROOT, 'vehiculos')
        if os.path.isdir(vehiculos_dir):
            for fname in os.listdir(vehiculos_dir):
                if 'gemini' in fname.lower():
                    logo_url = settings.MEDIA_URL + 'vehiculos/' + fname
                    break

    # ── AÑADIDO: contador del carrito ──────────────────────────────
    carrito_count = len(request.session.get('carrito', []))
    idioma = request.session.get('idioma', None)   # None = no elegido aún
    mostrar_selector = idioma is None
    # ───────────────────────────────────────────────────────────────

    return {
        'carnest_logo_url': logo_url,
        'carrito_count': carrito_count,
        'idioma': idioma,
        'mostrar_selector': mostrar_selector,  # ← disponible en todos los templates
    }