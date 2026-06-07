# pyright: reportAttributeAccessIssue=false
from typing import cast
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from core.permissions import IsClient, IsFrontDesk, IsOwner
from schedule.filters import AssignmentFilterSet, AvailabilityFilterSet, AvailabilityPresentationAssignmentFilterSet, AvailabilityPresentationFilterSet, AvailabilityPresentationOccupationFilterSet, ResourceFilterSet, ServiceFilterSet, ServiceRequirementsFilterSet, TimeBlockFilterSet
from schedule.models import Assignment, Availability, Resource, ResourceNotSelectable, ResourceObject, ResourceOccupation, ResourceSelectable, Service, ServiceResourceRelation, TimeBlock
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
        ServiceSerializer,
        TimeBlockSerializer
    )
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from schedule.utils import ResourceOcuppied, slot_to_time

# Create your views here.
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilterSet

    def handle_exception(self, exc):
        from django.core.exceptions import ValidationError
        try:
            return super().handle_exception(exc)
        except ValidationError as e:
            return Response(e.message_dict, 400)

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
    viewsets.mixins.RetrieveModelMixin,
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
        except IntegrityError as e:
            return Response('Erro de concorrência ao registrar o recurso. Tente novamente.', 422)

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
    permission_classes = [
        IsOwner | IsFrontDesk | (
            IsClient & IsAuthenticatedOrReadOnly
        )
    ]

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

    @action(["GET"], True)
    def ticker_download(self, request, pk):
        from weasyprint import HTML
        obj = cast(Assignment,self.get_object())
        html_string = render_to_string(
            'components/ticker.html',
            {
                'client_name': self.request.user.get_full_name(),
                'emission': obj.created,
                'appointment_uuid': str(obj.uuid)[:8],
                'appointment_date': obj.date,
                'appointment_start': slot_to_time(obj.start_slot),
                'appointment_end': slot_to_time(obj.duration_slot + obj.start_slot),
                'resources': obj.resources.all(),
                'service_name': obj.service.title if obj.service else ""
            }
        )
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = f'inline; filename="ticker_{obj.uuid}.pdf"'
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
        return response

    def get_queryset(self):
        if self.action == "ticker_download":
            content_type = ContentType.objects.get_for_model(self.request.user)
            return super().get_queryset().filter(
                resources__content_type=content_type,
                resources__object_id=self.request.user.pk,
            )
            
        return super().get_queryset()

    
class ClientAssignmentViewSet(BaseAssignmentViewSet):
    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(self.request.user)
        object_id = self.request.user.id

        return super().get_queryset().filter(
            resources__content_type=content_type,
            resources__object_id=object_id            
        )
    
    def perform_create(self, serializer):
        client_type, c = ResourceNotSelectable.objects.get_or_create(
            code="client",
            defaults={
                'is_selectable': False,
                'name': _('Client'),
            }
        )

        content_type = ContentType.objects.get_for_model(self.request.user)
        object_id = self.request.user.id
    
        user_resource, c = ResourceSelectable.objects.get_or_create(
            parent=client_type,
            content_type=content_type,
            object_id=object_id,
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
        current_time = self.request.query_params.get("current_time", None)

        occupation_filterset = AvailabilityPresentationOccupationFilterSet(
            {
                **self.request.query_params.dict(),
                'date_after': dt_after,
                'date_before': dt_after,
                'day': date,
            },
            ResourceOccupation.objects.all(),
        )
        if not occupation_filterset.is_valid():
            raise self.AssignmentFilterSetError(occupation_filterset.errors)

        if date:
            dt_before = date
            dt_after = date

        context.update({
            'occupations': list(occupation_filterset.qs),
            'dt_before': dt_before,
            'dt_after': dt_after,
            'current_time': current_time,
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


class TimeBlockViewSet(viewsets.ModelViewSet):
    queryset = TimeBlock.objects.all()
    serializer_class = TimeBlockSerializer
    filterset_class = TimeBlockFilterSet

    @transaction.atomic
    def perform_create(self, serializer):
        return super().perform_create(serializer)

    @transaction.atomic
    def perform_update(self, serializer):
        return super().perform_update(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)
