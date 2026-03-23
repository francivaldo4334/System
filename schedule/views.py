# pyright: reportAttributeAccessIssue=false
from django.shortcuts import render
from rest_framework import viewsets

from schedule.models import ResourceSelectable, Service
from schedule.serializers import ResourcesSerializer, ServiceSerializer

# Create your views here.
class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset =ResourceSelectable.objects.all()
    serializer_class = ResourcesSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


# class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Appointment.objects.all()
#     serializer_class = AssignmentSlotSerializer
#     filterset_class = AssignmentSlotFilterSet
