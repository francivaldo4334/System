from rest_framework import viewsets

from core.permissions import IsOwner
from django.apps import apps
from django.conf import settings

from core.serializers import UserSerializer

UserModel = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()
