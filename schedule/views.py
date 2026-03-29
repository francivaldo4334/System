# pyright: reportAttributeAccessIssue=false
from django.shortcuts import render
from rest_framework import viewsets

from schedule.models import Assignment, ResourceNotSelectable, ResourceSelectable, Service
from schedule.serializers import AssignmentSerializer, CreateAssigmentSerializer, ResourcesSerializer, ServiceSerializer

# Create your views here.
class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset =ResourceNotSelectable.objects.all()
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
