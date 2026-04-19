# pyright: reportAttributeAccessIssue=false
from django.db.models.deletion import ProtectedError
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView
from schedule.filters import AvailabilityPresentationFilterSet, ResourceFilterSet
from schedule.models import Assignment, Availability, Resource, Service, ServiceResourceRelation
from schedule.serializers import (
        AssignmentSerializer,
        AvailabilityPresentationSerializer,
        AvailabilitySerializer,
        CreateAssigmentSerializer,
        ResourceSerializer,
        ServiceResourceRelationSerializer,
        ServiceSerializer
    )
from django.utils.translation import gettext_lazy as _

# Create your views here.
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilterSet

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            error = APIException(_("Deletion of %(name)s failed") % {'name': instance._meta.verbose_name})
            error.status_code = 409
            raise error

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceRequirementsViewSet(viewsets.ModelViewSet):
    queryset = ServiceResourceRelation.objects.all()
    serializer_class = ServiceResourceRelationSerializer

# pyright:reportIncompatibleMethodOverride=false
class AssignmentViewSet(viewsets.mixins.ListModelMixin,
                        viewsets.mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = Assignment.objects.all().select_related('service').prefetch_related('resources')
    serializer_class = AssignmentSerializer
    # filterset_class = AssignmentSlotFilterSet

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAssigmentSerializer
        return super().get_serializer_class()


class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

class AvailabilityPresentationAPIView(ListAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilityPresentationSerializer
    filterset_class = AvailabilityPresentationFilterSet
    pagination_class = None
