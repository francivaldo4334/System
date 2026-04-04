# pyright: reportAttributeAccessIssue=false
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from schedule.filters import AvailabilityFilterSet
from schedule.models import Assignment, Availability, ResourceSelectable, Service
from schedule.serializers import AssignmentSerializer, AvailabilityPresentationSerializer, AvailabilitySerializer, CreateAssigmentSerializer, ResourcesSerializer, ServiceSerializer

# Create your views here.
class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset =ResourceSelectable.objects.all()
    serializer_class = ResourcesSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


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
    @property
    def filterset_class(self):
        return AvailabilityFilterSet

    def get_serializer_class(self):
        if self.action == "presentation":
            return AvailabilityPresentationSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "presentation":
            resource = get_object_or_404(ResourceSelectable, pk=self.kwargs.get("pk", None))
            return queryset.filter(resource=resource)

        return queryset
    @action(["GET"], True)
    def presentation(self, request, pk):
        return super().list(request, pk)
