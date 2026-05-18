"""
CarNest/settings_prod.py
------------------------
Configuración de producción para GCP.
Extiende settings.py base con ajustes seguros para producción.

Uso: el docker-compose.prod.yml setea DJANGO_SETTINGS_MODULE=CarNest.settings_prod
"""
from CarNest.settings import *
import os

# ── Seguridad ─────────────────────────────────────────────────────
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# ── Archivos estáticos ────────────────────────────────────────────
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = '/static/'

MEDIA_ROOT = '/app/media'
MEDIA_URL = '/media/'

# ── Seguridad adicional en producción ─────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = False   # Cambiar a True si usas HTTPS
CSRF_COOKIE_SECURE = False      # Cambiar a True si usas HTTPS

# ── Logging ───────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
