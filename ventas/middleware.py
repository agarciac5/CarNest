from django.conf import settings
from django.utils.translation import activate
from django.http import HttpResponseRedirect
from urllib.parse import urlparse


class IdiomaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ── 1. Capturar nueva elección de idioma ──────────────────────
        if request.method == 'POST' and request.POST.get('_set_idioma'):
            idioma = request.POST.get('idioma', 'es')
            if idioma not in ('es', 'en'):
                idioma = 'es'

            request.session['idioma'] = idioma

            # Obtener el path actual desde el Referer
            url_actual = request.META.get('HTTP_REFERER', '/')
            path_actual = urlparse(url_actual).path

            # Normalizar: quitar prefijo de idioma existente para obtener path base
            path_base = path_actual
            for lang_code in ('en', 'es'):
                if path_actual.startswith(f'/{lang_code}/'):
                    path_base = path_actual[len(f'/{lang_code}'):]
                    if not path_base.startswith('/'):
                        path_base = '/' + path_base
                    break
                elif path_actual == f'/{lang_code}':
                    path_base = '/'
                    break

            # Construir URL destino
            # Con prefix_default_language=False:
            #   español → sin prefijo → /inventario/1/
            #   inglés  → con prefijo → /en/inventario/1/
            if idioma == 'en':
                redirect_url = f'/en{path_base}'
            else:
                redirect_url = path_base

            activate(idioma)
            request.LANGUAGE_CODE = idioma

            response = HttpResponseRedirect(redirect_url)
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                idioma,
                max_age=365 * 24 * 60 * 60,
            )
            return response

        # ── 2. Aplicar idioma guardado en sesión en cada request ──────
        idioma_sesion = request.session.get('idioma')
        if idioma_sesion in ('es', 'en'):
            activate(idioma_sesion)
            request.LANGUAGE_CODE = idioma_sesion

        response = self.get_response(request)

        # ── 3. Mantener cookie sincronizada ───────────────────────────
        if idioma_sesion in ('es', 'en'):
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                idioma_sesion,  # ← era 'idioma', variable no definida en GET normal
                max_age=365 * 24 * 60 * 60,
            )

        return response