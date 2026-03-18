from .base import INSTALLED_APPS
INSTALLED_APPS += [
    'drf_spectacular',
    'rest_framework',
]
# Django Restframework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 30,
}
