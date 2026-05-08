# pyright: reportAttributeAccessIssue=false
from datetime import timedelta
from django.db.models.deletion import ProtectedError
from django.utils.timezone import datetime
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from schedule.filters import AssignmentFilterSet, AvailabilityFilterSet, AvailabilityPresentationFilterSet, ResourceFilterSet, ServiceFilterSet, ServiceRequirementsFilterSet
from schedule.models import Assignment, Availability, Resource, ResourceOccupation, Service, ServiceResourceRelation
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
from rest_framework.decorators import action

from schedule.utils import ResourceOcuppied

# Create your views here.
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilterSet

    @action(["GET"], False)
    def unavailable_dates(self, request):
        now = datetime.now()
        occupieds = ResourceOccupation.objects.filter(
            date__range=(now, now + timedelta(days=30)),
        ).exclude(bitmap__icontains='0')
        return Response([o.date for o in occupieds])

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

    def handle_exception(self, exc):
        try:
            return super().handle_exception(exc)
        except ResourceOcuppied as e:
            return Response([_('Slot occupied')], 422)
        except NotImplementedError as e:
            return Response(e.args, 422)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAssigmentSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        if self.action == 'list':
            return super().filter_queryset(queryset)
        return super().get_queryset()

    @action(['POST'], True)
    def rescue(self, request, pk):
        obj = self.get_object()
        obj.state.rescue()
        return Response(self.get_serializer(obj).data)

    @action(['POST'], True)
    def confirm(self, request, pk):
        obj = self.get_object()
        obj.state.confirm()
        return Response(self.get_serializer(obj).data)

    @action(['POST'], True)
    def start(self, request, pk):
        obj = self.get_object()
        obj.state.start()
        return Response(self.get_serializer(obj).data)

    @action(['POST'], True)
    def finish(self, request, pk):
        obj = self.get_object()
        obj.state.finish()
        return Response(self.get_serializer(obj).data)

    @action(['POST'], True)
    def migrate(self, request, pk):
        obj = self.get_object()
        obj.state.migrate()
        return Response(self.get_serializer(obj).data)

    @action(['POST'], True)
    def cancel(self, request, pk):
        obj = self.get_object()
        obj.state.cancel()
        return Response(self.get_serializer(obj).data)

    @action(['POST'], True)
    def absent(self, request, pk):
        obj = self.get_object()
        obj.state.absent()
        return Response(self.get_serializer(obj).data)


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
            'assignments': Assignment.objects.filter(date=date).visibles()
        })
        return context;
