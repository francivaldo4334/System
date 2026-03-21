from django.urls import path, include
from rest_framework import routers

from schedule.views import AssignmentSlotViewSet, ResourceViewSet, ServiceViewSet

router = routers.SimpleRouter()

router.register('resources', ResourceViewSet, 'resources')
router.register('services', ServiceViewSet, 'services')
router.register('assigments', AssignmentSlotViewSet, 'assignments')


urlpatterns = [
    path('',include(router.urls))
]
