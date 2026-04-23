from django.shortcuts import render
from rest_framework import viewsets
from users.models import ClientBadge
from users.serializers import ClientBadgeSerializer

# Create your views here.
class ClientBagdeViewSet(viewsets.ModelViewSet):
    queryset = ClientBadge.objects.all();
    serializer_class = ClientBadgeSerializer
