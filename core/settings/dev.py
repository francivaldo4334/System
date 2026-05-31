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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
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
