from pathlib import Path

from django.conf import settings


def carnest_branding(_request):
    """
    URL del logo CarNest en media (archivo con 'gemini' en el nombre dentro de
    media/vehiculos/, o CARNEST_LOGO_PATH en settings).
    """
    media_url = settings.MEDIA_URL
    if not str(media_url).startswith('/'):
        media_url = '/' + str(media_url).lstrip('/')
    media_url = str(media_url).rstrip('/')

    preferred = getattr(settings, 'CARNEST_LOGO_PATH', None)
    if preferred:
        return {'carnest_logo_url': f'{media_url}/{str(preferred).lstrip("/")}'}

    veh = Path(settings.MEDIA_ROOT) / 'vehiculos'
    if veh.is_dir():
        for p in sorted(veh.iterdir()):
            if p.is_file() and 'gemini' in p.name.lower():
                return {'carnest_logo_url': f'{media_url}/vehiculos/{p.name}'}
    return {'carnest_logo_url': ''}
