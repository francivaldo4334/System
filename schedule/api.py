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

def create_resource_viewset(code):
    class DynamicResourceViewSet(ResourceViewSet):
        code_filter = code
    return DynamicResourceViewSet

resource_types = list(ResourceNotSelectable.objects.all())

for r in resource_types:
    DynamicViewSet = create_resource_viewset(r.code)
    router.register(f'resource/{r.code}', DynamicViewSet, basename=f'resource-{r.code}')


urlpatterns = [
    path('schedule/',include(router.urls)),
    path('schedule/availabilities_presentation', AvailabilityPresentationAPIView.as_view(), name="availabilities_presentation")
]
