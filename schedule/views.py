# pyright: reportAttributeAccessIssue=false
from django.shortcuts import render
from rest_framework import viewsets

from schedule.models import Resource
from schedule.serializers import ResourcesSerializer

# Create your views here.
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = ResourcesSerializer
