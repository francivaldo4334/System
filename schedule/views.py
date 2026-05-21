# pyright: reportAttributeAccessIssue=false
from datetime import timedelta
from typing import Self, Type, cast
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError
from django.utils.timezone import datetime
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
from rest_framework.response import Response
from core.permissions import IsFrontDesk, IsOwner
from schedule.filters import AssignmentFilterSet, AvailabilityFilterSet, AvailabilityPresentationAssignmentFilterSet, AvailabilityPresentationFilterSet, ResourceFilterSet, ServiceFilterSet, ServiceRequirementsFilterSet
from schedule.models import Assignment, Availability, Resource, ResourceNotSelectable, ResourceObject, ResourceOccupation, ResourceSelectable, Service, ServiceResourceRelation
from schedule.serializers import (
        ActionMigrateSerializer,
        AssignmentSerializer,
        AvailabilityPresentationSerializer,
        AvailabilitySerializer,
        CreateAssigmentSerializer,
        DashboardSerializer,
        ResourceObjectSerializer,
        ResourcePersonSerializer,
        ResourceSerializer,
        ServiceResourceRelationSerializer,
        ServiceSerializer
    )
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from schedule.utils import ResourceOcuppied

# Create your views here.
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilterSet

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError:
            error = APIException(_("This item already exists."))
            error.status_code = 409
            raise error
    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            error = APIException(_("Deletion of %(name)s failed") % {'name': instance._meta.verbose_name})
            error.status_code = 409
            raise error
class DynamicResourceViewSet(ResourceViewSet):
    serializer_class = ResourceObjectSerializer

    def get_serializer_class(self):
        parent = get_object_or_404(ResourceNotSelectable,code=self.code_filter)

        if parent.content_type:
            from django.apps import apps
            from django.conf import settings
            user_model = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
            content_type = ContentType.objects.get_for_model(user_model)
            if parent.content_type == content_type:
                return ResourcePersonSerializer
        return super().get_serializer_class()
    @property
    def code_filter(self):
        """
        Captura o código dinamicamente da URL caso a rota coringa seja acessada.
        Se acessar a rota padrão de resources, retorna None.
        """
        return self.kwargs.get('resource_code')

    def get_queryset(self):
        return super().get_queryset().filter(parent__code=self.code_filter)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'parent_code': self.code_filter
        })
        return context

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filterset_class = ServiceFilterSet

class ServiceRequirementsViewSet(viewsets.ModelViewSet):
    queryset = ServiceResourceRelation.objects.all()
    serializer_class = ServiceResourceRelationSerializer
    filterset_class = ServiceRequirementsFilterSet

# pyright:reportIncompatibleMethodOverride=false
class BaseAssignmentViewSet(
    viewsets.mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
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
    
class AssignmentViewSet(viewsets.mixins.ListModelMixin,
                        BaseAssignmentViewSet):
    permission_classes = [IsOwner | IsFrontDesk]

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
    @extend_schema(
        request=ActionMigrateSerializer(),
    )
    def migrate(self, request, pk):
        obj = cast(Assignment,self.get_object())
        serializer = ActionMigrateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        start_slot = validated_data['start_slot']
        duration_slot = validated_data['duration_slot']
        new_date = validated_data['date']
        obj.state.migrate(start_slot, duration_slot, new_date, request.user)
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

    
class ClientAssignmentViewSet(BaseAssignmentViewSet):
    def perform_create(self, serializer):
        client_type, c = ResourceNotSelectable.objects.get_or_create(
            code="client",
            defaults={
                'is_selectable': False,
                'name': _('Client'),
            }
        )
    
        user_resource, c = ResourceSelectable.objects.get_or_create(
            parent=client_type,
            content_type=ContentType.objects.get_for_model(self.request.user),
            object_id=self.request.user.id,
            defaults={
                'name': self.request.user.get_full_name,
                'is_selectable': True,
                'code':f'client.{self.request.user.username}',
            }
        )
        serializer.save(user_client_resource=user_resource)

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    filterset_class = AvailabilityFilterSet


class AvailabilityPresentationAPIView(ListAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilityPresentationSerializer
    filterset_class = AvailabilityPresentationFilterSet
    pagination_class = None

    class AssignmentFilterSetError(Exception):
        pass

    def handle_exception(self, exc):
        try:
            return super().handle_exception(exc)
        except self.AssignmentFilterSetError as e:
            return Response(e.args[0], 400)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        dt_before = self.request.query_params.get('date_before', None)
        dt_after = self.request.query_params.get('date_after', None)
        date = self.request.query_params.get('day', None)
        assignment_filterset = AvailabilityPresentationAssignmentFilterSet(
            {
                **self.request.query_params,
                'date_after': dt_after,
                'date_before': dt_after,
                'day': date,
            },
            Assignment.objects.filter(date=date).visibles()
        )
        if not assignment_filterset.is_valid():
            raise self.AssignmentFilterSetError(assignment_filterset.errors)

        if date:
            dt_before = date
            dt_after = date

        context.update({
            'assignments': assignment_filterset.qs,
            'dt_before': dt_before,
            'dt_after': dt_after,
        })
        return context;

class DashboardAPIView(GenericAPIView):
    queryset = Assignment.objects.all()
    serializer_class = DashboardSerializer
    filterset_fields = [
        'date',
        'status',
        'service',
        'resources__parent',
        'resources',
    ]
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset()).values(
            'status'
        ).annotate(total=Count('status'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
