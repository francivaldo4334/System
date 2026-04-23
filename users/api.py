from django.urls import include, path
from rest_framework import routers

from users.views import CustomerBagdeViewSet, TeamBadgeViewSet
router = routers.SimpleRouter()
router.register('customers_badges',CustomerBagdeViewSet, 'customers_badges')
router.register('team_badges',TeamBadgeViewSet, 'team_badges')

urlpatterns = [
    path('', include(router.urls)),
]
