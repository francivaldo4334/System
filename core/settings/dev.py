from .base import *
from .ssr import *
from .api import *

DEBUG = True

INSTALLED_APPS += [
    'drf_spectacular',
]

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'core.urls.dev'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'
