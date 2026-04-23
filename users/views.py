from django.shortcuts import render
from rest_framework import viewsets
from users.models import CustomerBadge, TeamBadge
from users.serializers import BadgeSerializer

# Create your views here.
class CustomerBagdeViewSet(viewsets.ModelViewSet):
    queryset = CustomerBadge.objects.all();
    serializer_class = BadgeSerializer;

class TeamBadgeViewSet(viewsets.ModelViewSet):
    queryset = TeamBadge.objects.all();
    serializer_class = BadgeSerializer;
