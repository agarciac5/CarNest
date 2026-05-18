import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-only-change-me')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '34.27.19.160']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core.apps.CoreConfig',
    'anuncios',
    'inventario',
    'usuarios',
    'ventas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',        # ← NUEVO i18n
    'ventas.middleware.IdiomaMiddleware',               # ← NUEVO overlay
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CarNest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.i18n',  # ← NUEVO
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.carnest_branding',
            ],
        },
    },
]

WSGI_APPLICATION = 'CarNest.wsgi.application'

_postgres_db = os.environ.get('POSTGRES_DB')
if _postgres_db:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _postgres_db,
            'USER': os.environ.get('POSTGRES_USER', 'carnest'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'carnest'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── i18n real ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'es'

LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'UTC'
# ───────────────────────────────────────────────────────────────────

STATIC_URL = 'static/'
STATIC_ROOT = '/app/staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CARNEST_LOGO_PATH = ''

LOGIN_URL = 'login'          # nombre de la URL, no path
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTH_USER_MODEL = 'usuarios.Usuario'

# ── Stripe (pasarela de pagos) ──────────────────────────────────────────────
# Crea tu cuenta en https://dashboard.stripe.com y consigue las claves en:
# Dashboard → Developers → API keys
#
# En desarrollo, las claves de PRUEBA empiezan con sk_test_ y pk_test_
# NUNCA pongas la clave secreta directamente en código; usa variables de entorno.
STRIPE_PUBLIC_KEY   = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY   = os.environ.get('STRIPE_SECRET_KEY')


