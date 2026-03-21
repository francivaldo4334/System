from .base import INSTALLED_APPS
INSTALLED_APPS += [
    'rest_framework',
    'schedule',
    'sale',
    'stock',
]
# Django Restframework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
