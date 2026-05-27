from django.urls import path, include
from rest_framework import routers
from core.views import UserViewSet

router = routers.SimpleRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include('schedule.api')),
    path('', include(router.urls)),
]
