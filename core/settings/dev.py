from .base import *
from .ssr import *
from .api import *
from decouple import config, Csv

DEBUG = True

INSTALLED_APPS += [
    'drf_spectacular',
    'django_browser_reload',
]

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'core.urls.dev'

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME','ponto_agio_prod'),
        'USER': config('DB_USER', 'ponto_agio_admin'),
        'PASSWORD': config('DB_PASSWORD','uma_senha_forte_aqui'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='5432', cast=int),
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'
MIDDLEWARE += [
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
