from django.urls import path, include
from rest_framework import routers

from schedule.models import ResourceNotSelectable
from schedule.views import AssignmentViewSet, AvailabilityPresentationAPIView, AvailabilityViewSet, ClientAssignmentViewSet, ResourceViewSet, ServiceRequirementsViewSet, ServiceViewSet

router = routers.SimpleRouter()

router.register('resources', ResourceViewSet, 'resources')
router.register('services', ServiceViewSet, 'services')
router.register('service_requirements', ServiceRequirementsViewSet, 'service_requirements')
router.register('assignment', AssignmentViewSet, 'assignment')
router.register('client/assignment', ClientAssignmentViewSet, 'client_assignment')
router.register('availabilities', AvailabilityViewSet, 'availabilities')

dynamic_resource_list = ResourceViewSet.as_view({'get': 'list', 'post': 'create'})
dynamic_resource_detail = ResourceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = [
    path('schedule/',include(router.urls)),
    path('schedule/availabilities_presentation', AvailabilityPresentationAPIView.as_view(), name="availabilities_presentation"),
    # Rotas dinâmicas que capturam o 'resource_code' e passam para a ViewSet
    path('schedule/resource/<str:resource_code>/', dynamic_resource_list, name='dynamic-resource-list'),
    path('schedule/resource/<str:resource_code>/<int:pk>/', dynamic_resource_detail, name='dynamic-resource-detail'),
]
