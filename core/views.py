from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView
from rest_framework import viewsets

from core.permissions import IsOwner
from django.apps import apps
from django.conf import settings

from core.serializers import UserSerializer

UserModel = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all().filter(is_superuser=False)

class LandingPageView(TemplateView):
    template_name = "pages/landing-page/index.html"

def is_not_tenant_master(view):
    def _view(request, *args, **kwargs):
        if not request.tenant.is_master:
            return view(request, *args, **kwargs)
        return redirect(reverse('home'))
    return _view
