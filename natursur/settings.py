from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
load_dotenv(BASE_DIR / '.env')

# En producción, usar variable de entorno; en desarrollo, usar valor por defecto
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-replace-this-for-prod')

# DEBUG basado en variable de entorno (por defecto True en desarrollo)
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# ALLOWED_HOSTS: permitir render.com y localhost
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
# Limpiar espacios en blanco
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reservas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'natursur.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # app templates are used
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'natursur.context_processors.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'natursur.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_TZ = True

# Static files configuration para Render
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# After login redirect to home by default
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# URL externa de la tienda
EXTERNAL_SHOP_URL = 'https://natursur.herbalife.com/es-es/u'

# Redes sociales
# ID del canal de YouTube de @natursur (para feed RSS)
YOUTUBE_CHANNEL_ID = 'UCryL5eZosDAQ4fDHuXK8pvw'
# Username de Instagram para scrapear posts públicos (usando instagrapi)
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', 'yosoyescalona')

# Security settings para producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
    }

# Email configuration
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Resend API en producción (v2.x)
    pass

RESEND_API_KEY = os.getenv('RESEND_API_KEY', None)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@natursur.com')
