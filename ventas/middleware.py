class IdiomaMiddleware:
    """
    Si la sesión no tiene idioma definido, fuerza mostrar el selector.
    Guarda la elección en request.session['idioma'] ('es' o 'en').
    Persiste hasta que el servidor se reinicia (sesión de Django).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capturar elección si viene del formulario del selector
        if request.method == 'POST' and request.POST.get('_set_idioma'):
            idioma = request.POST.get('idioma', 'es')
            if idioma in ('es', 'en'):
                request.session['idioma'] = idioma
                request.session.modified = True

        response = self.get_response(request)
        return response