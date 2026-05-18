import os
from django.conf import settings
from django.utils import translation


def carnest_branding(request):
    logo_url = None
    logo_path_setting = getattr(settings, 'CARNEST_LOGO_PATH', '')

    if logo_path_setting:
        logo_url = settings.MEDIA_URL + logo_path_setting
    else:
        vehiculos_dir = os.path.join(settings.MEDIA_ROOT, 'vehiculos')
        if os.path.isdir(str(vehiculos_dir)):
            for fname in os.listdir(str(vehiculos_dir)):
                if 'gemini' in fname.lower():
                    logo_url = settings.MEDIA_URL + 'vehiculos/' + fname
                    break

    carrito_count = len(request.session.get('carrito', []))

    # Leer idioma desde sesión (nuestro overlay) o desde Django i18n
    idioma = request.session.get('idioma') or translation.get_language() or 'es'
    mostrar_selector = 'idioma' not in request.session

    return {
        'carnest_logo_url': logo_url,
        'carrito_count': carrito_count,
        'idioma': idioma,
        'mostrar_selector': mostrar_selector,
    }