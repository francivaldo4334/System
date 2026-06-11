from .base import *
from .ssr import *
from .api import *
from decouple import config, Csv
from pathlib import Path

# Configurações Principais
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
ROOT_URLCONF = 'core.urls.dev'

# Banco de Dados
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql',
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='5432', cast=int),
    }
}
# Configurações de E-mail (SES)
EMAIL_BACKEND = 'django_ses.SESBackend'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION_NAME', 'us-east-1')
AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'

# Configurações de Remetente Padrão (OBRIGATÓRIO usar o domínio validado)
DEFAULT_FROM_EMAIL = 'Suporte Ponto Ágio <suporte@pontoagio.com.br>'
SERVER_EMAIL = 'notificacoes@pontoagio.com.br'
# Configurações de E-mail (SMTP)
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/mediafiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
CELERY_BROKER_URL = f"redis://:{os.environ.get('REDIS_PASSWORD')}@redis:6379/0"
CELERY_RESULT_BACKEND = f"redis://:{os.environ.get('REDIS_PASSWORD')}@redis:6379/0"
