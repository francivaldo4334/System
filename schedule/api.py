from django.urls import path, include
from rest_framework import routers

from schedule.views import ResourceViewSet

router = routers.SimpleRouter()

router.register('resources', ResourceViewSet, 'resources')


urlpatterns = [
    path('',include(router.urls))
]
