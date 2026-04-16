# pyright: reportAttributeAccessIssue=false
from django.db import transaction
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from schedule.filters import AvailabilityPresentationFilterSet, ResourceFilterSet
from schedule.models import Assignment, Availability, Resource, Service, ServiceResourceRelation
from schedule.serializers import AssignmentSerializer, AvailabilityPresentationSerializer, AvailabilitySerializer, CreateAssigmentSerializer, ResourceSerializer, ServiceResourceRelationSerializer, ServiceSerializer

# Create your views here.
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilterSet


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
