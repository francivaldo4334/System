from django.urls import path, include
from rest_framework import routers

from schedule.views import ResourceViewSet, ServiceViewSet

router = routers.SimpleRouter()

router.register('resources', ResourceViewSet, 'resources')
router.register('services', ServiceViewSet, 'services')


urlpatterns = [
    path('',include(router.urls))
]
