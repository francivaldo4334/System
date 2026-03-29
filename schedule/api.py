from django.urls import path, include
from rest_framework import routers

from schedule.views import AssignmentViewSet, AvailabilityViewSet, ResourceViewSet, ServiceViewSet

router = routers.SimpleRouter()

router.register('resources', ResourceViewSet, 'resources')
router.register('services', ServiceViewSet, 'services')
router.register('assignment', AssignmentViewSet, 'assignment')
router.register('availabilities', AvailabilityViewSet, 'availabilities')


urlpatterns = [
    path('schedule/',include(router.urls))
]
