# pyright: reportAttributeAccessIssue=false
from django.shortcuts import render
from rest_framework import viewsets

from schedule.models import AssignmentSlot, Resource, Service
from schedule.serializers import AssignmentSlotSerializer, ResourcesSerializer, ServiceSerializer

# Create your views here.
class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = ResourcesSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class AssignmentSlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssignmentSlot.objects.all()
    serializer_class = AssignmentSlotSerializer
