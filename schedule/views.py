# pyright: reportAttributeAccessIssue=false
from django.db.models.deletion import ProtectedError
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView
from schedule.filters import AssignmentFilterSet, AvailabilityFilterSet, AvailabilityPresentationFilterSet, ResourceFilterSet, ServiceFilterSet, ServiceRequirementsFilterSet
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
    filterset_class = ServiceFilterSet

class ServiceRequirementsViewSet(viewsets.ModelViewSet):
    queryset = ServiceResourceRelation.objects.all()
    serializer_class = ServiceResourceRelationSerializer
    filterset_class = ServiceRequirementsFilterSet

# pyright:reportIncompatibleMethodOverride=false
class AssignmentViewSet(viewsets.mixins.ListModelMixin,
                        viewsets.mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = Assignment.objects.all().select_related('service').prefetch_related('resources')
    serializer_class = AssignmentSerializer
    filterset_class = AssignmentFilterSet

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAssigmentSerializer
        return super().get_serializer_class()


class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    filterset_class = AvailabilityFilterSet

class AvailabilityPresentationAPIView(ListAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilityPresentationSerializer
    filterset_class = AvailabilityPresentationFilterSet
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        date = self.request.query_params.get('date')
        context.update({
            'assignments': Assignment.objects.filter(date=date)
        })
        return context;
