from django.urls import include, path
from rest_framework import routers

from users.views import ClientBagdeViewSet
router = routers.SimpleRouter()
router.register('clients',ClientBagdeViewSet, 'clients')

urlpatterns = [
    path('', include(router.urls)),
]
