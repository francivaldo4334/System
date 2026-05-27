from dataclasses import dataclass
from typing import List, Type
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from app.forms import AssignmentForm, AvailabilityForm, BaseForm, CustomUserCreationForm, ResourceForm, ResourcePersonForm, ServiceForm, ServiceRequirementsForm, UserForm
from app.models import AppConfig
from app.serializers import AppConfigSerializer
from app.tables import AvailabilityTable, BaseTable, ResourcesTable, ServiceRequirementsTable, ServicesTable, Table, UserTable
from core.permissions import IsFrontDesk, IsOnlyClient, IsOwner, IsProfessional


class AppView(PermissionRequiredMixin,
              LoginRequiredMixin,
              TemplateView):
    template_name = "pages/app/index.html"

    def is_owner(self):
        return IsOwner().has_permission(self.request, None)

    def is_front_desk(self):
        return IsFrontDesk().has_permission(self.request, None)

    def is_professinal(self):
        return IsProfessional().has_permission(self.request, None)

    def has_permission(self):
        allowed = (
            self.is_owner() or\
            self.is_front_desk() or\
            self.is_professinal()
        )
        return allowed 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_template_name_options = []

        if self.is_owner() or self.is_front_desk() or self.is_professinal():
            app_template_name_options.append({
                'url_name': 'app-schedule',
                'title': _('Agenda'),
                'icon_template_name': 'icons/calendar.svg'
            })
        if self.is_owner():
            app_template_name_options.append({
                'url_name': 'app-schedule-settings',
                'title': _('Settings'),
                'icon_template_name': 'icons/calendar-cog.svg'
            })
            

        context.update({
            'app_template_name_options': app_template_name_options,
            'defaultday': f'{timezone.localtime(timezone.now()).date().isoformat()}T00:00:00',
        })
        return context
    def get_template_names(self):
        if self.request.META.get('HTTP_AJAX_REQUEST', False):
            self.template_name += "#main"
        return super().get_template_names()

class AppScheduleView(AppView):
    template_name = 'pages/app/schedule/index.html'
    # extra_context = {
    #     'assignment_form': AssignmentForm
    # }
class AppScheduleSettingsView(AppView):
    template_name = 'pages/app/schedule/settings/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'setting_tag_selected': '',
        })
        user = self.request.user
        setting_tabs = []

        if user.has_perm('schedule.view_availability'):
            setting_tabs.append({
                'label': _("Availabilities"),
                'url_name': 'app-schedule-settings-availabilities',
                'is_dynamic': False,  # Flag útil para o template diferenciar as URLs
            })
            context.update({
                'setting_tag_selected': 'app-schedule-settings-availabilities',
            })

        if user.has_perm('schedule.view_resource'):
            from schedule.models import ResourceObject, ResourcePerson
            
            # 1. Recursos do tipo Objeto
            # object_options = ScheduleSettingsResourceView.get_options()
            resources_object = ResourceObject.objects.filter(is_selectable=False)
            for it in resources_object:
                setting_tabs.append({
                    'label': it.name,
                    'url_name': 'app-schedule-settings-resource-object',  # Nome base estático da rota
                    'url_kwargs': {'key': it.code},  # Dicionário de argumentos que a rota exige
                    'is_dynamic': True,
                })

            # 2. Recursos do tipo Pessoa
            # person_options = ScheduleSettingsResourcePersonView.get_options()
            resources_person = ResourcePerson.objects.filter(is_selectable=False)
            for it in resources_person:
                setting_tabs.append({
                    'label': it.name,
                    'url_name': 'app-schedule-settings-resource-person',  # Nome base estático da rota
                    'url_kwargs': {'key': it.code},  # Dicionário de argumentos que a rota exige
                    'is_dynamic': True,
                })

        if user.has_perm('schedule.view_service'):
            setting_tabs.append({
                'label': _("Services"),
                'url_name': 'app-schedule-settings-services',
                'is_dynamic': False,
            })
        if user.has_perm('schedule.view_users'):
            setting_tabs.append({
                'label': _("Users"),
                'url_name': 'app-schedule-settings-users',
                'is_dynamic': False,
            })

        # if user.has_perm('schedule.view_serviceresourcerelation'):
        #     setting_tabs.append({
        #         'label': _("Service Requirements"),
        #         'url_name': 'app-schedule-settings-service-requirements',
        #         'is_dynamic': False,
        #     })

        context.update({
            'setting_tabs': setting_tabs
        })
        return context

class CrudView(LoginRequiredMixin, TemplateView):
    template_name = 'layouts/crud/index.html'
    key: str
    form: Type[BaseForm]
    table: Type[BaseTable]
    model_name: str = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form_instance = self.form()
        
        context.update({
            'key': self.key,
        })
        user = self.request.user

        if user.has_perm(f'schedule.view_{self.model_name}'):
            context.update({
               'list': {
                   'table': self.table,
                }
            })

        if user.has_perm(f'schedule.change_{self.model_name}'):
            context.update({
               'update': {
                    'form': form_instance,
                    'update_url_name': f'{self.key}-detail'
                },
            })

        if user.has_perm(f'schedule.add_{self.model_name}'):
            context.update({
                'create': {
                    'form': form_instance,
                    'post_url_name': f'{self.key}-list',
                },
            })

        if user.has_perm(f'schedule.delete_{self.model_name}'):
            context.update({
                'delete': {
                    'delete_url_name': f'{self.key}-detail',
                },
            })
        return context

class ScheduleSettingsAvailabilitiesView(CrudView):
    key = 'availabilities'
    model_name = 'availability'
    form = AvailabilityForm
    table = AvailabilityTable

class ScheduleSettingsResourceView(CrudView):
    key = 'resources'
    model_name = 'resource'
    form = ResourceForm
    table = ResourcesTable

    def setup(self, request, *args, **kwargs):
        """
        Executado em tempo de requisição. Captura o '<str:key>' vindo da URL
        e customiza a tabela e as chaves de contexto dinamicamente.
        """
        super().setup(request, *args, **kwargs)
        
        # Se veio uma chave na URL, reconfigura a view para essa request
        url_key = self.kwargs.get('key')
        if url_key:
            # Mantém o isolamento criando uma subclasse da tabela em tempo de execução
            class CustomTable(self.table):
                pass
            CustomTable.key = f'dynamic-resource'
            
            self.key = f'dynamic-resource'
            self.table = CustomTable

class ScheduleSettingsResourcePersonView(ScheduleSettingsResourceView):
    form = ResourcePersonForm
    # Herda o comportamento dinâmico de setup() automaticamente

class ScheduleSettingsServiceView(CrudView):
    key = 'services'
    model_name = 'service'
    form = ServiceForm
    table = ServicesTable
class SettingsUserView(CrudView):
    key = "users"
    model_name = 'user'
    form = UserForm
    table = UserTable

class ScheduleSettingsServiceRequirementsView(CrudView):
    key = 'service_requirements'
    model_name = 'serviceresourcerelation'
    form = ServiceRequirementsForm
    table = ServiceRequirementsTable

# class SelfSchedulingView(LoginRequiredMixin, TemplateView):
#     template_name = 'pages/app/self_scheduling/index.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         config = AppConfig.objects.first()
#         context.update({
#             'config': config,
#             'steps': [{
#                 'step': i,
#                 **step
#             } for i,step in enumerate([
#                 {
#                     'icon': 'icons/house.svg',
#                     'template': 'pages/app/self_scheduling/home.html',
#                     'context': None
#                 },

#                 {
#                     'icon': 'icons/notebook-pen.svg',
#                     'template': 'pages/app/self_scheduling/services.html',
#                     'context': None
#                 },
#             # ] + [ {
#             #         'icon': 'icons/notebook-pen.svg',
#             #         'template': 'pages/app/self_scheduling/resource.html',
#             #         'context': it
#             # } for it in (config.resources_visibles.all() if config else [])
#             # ] + [
#                 {
#                     'icon': 'icons/calendar.svg',
#                     'template': 'pages/app/self_scheduling/dates.html',
#                     'context': None
#                 },
#                 {
#                     'icon': 'icons/clipboard-clock.svg',
#                     'template': 'pages/app/self_scheduling/times.html',
#                     'context': None
#                 },
#                 {
#                     'icon': 'icons/check-check.svg',
#                     'template': 'pages/app/self_scheduling/confirm.html',
#                     'context': None
#                 },
#             ])]
#         })
#         return context;

from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

class SelfScheduleView(LoginRequiredMixin, TemplateView):
    # Mapeamento de templates para fácil expansão
    STEP_TEMPLATES = {
        0: 'pages/app/self_scheduling/home.html',
        1: 'pages/app/self_scheduling/services.html',
        2: 'pages/app/self_scheduling/resource.html',
        3: 'pages/app/self_scheduling/dates.html',
        4: 'pages/app/self_scheduling/times.html',
        5: 'pages/app/self_scheduling/confirm.html',
    }

    @property
    def step(self):
        try:
            return int(self.request.GET.get('step', 0))
        except (ValueError, TypeError):
            return 0

    @property
    def template_name(self):
        template = self.STEP_TEMPLATES.get(self.step, self.STEP_TEMPLATES[0])
        return template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dispatcher simples baseado no step
        if self.step == 0:
            context['config'] = AppConfig.objects.first()
            
        elif self.step == 2:
            context.update(self._get_resource_step_context())

        elif self.step == 5:
            from schedule.models import Service, Resource
            service = get_object_or_404(Service, pk=self.request.GET.get('service', 0))
            resources = Resource.objects.filter(pk__in=self.request.GET.get('resource', '').split(','))
            context.update(
                {
                    'service': service,
                    'resources': resources
                }
            )

        return context

    def _get_resource_step_context(self):
        """Encapsula a lógica complexa do Step 2 sem alterar o funcionamento."""
        from schedule.models import Service, ResourceSelectable
        
        service_pk = self.request.GET.get('service', 0)
        service = get_object_or_404(Service, pk=service_pk)
        
        # Filtro de recursos necessários
        required_resources = list(service.required_resources.exclude(code__icontains='client'))
        total_resources = len(required_resources)
        
        try:
            current_idx = int(self.request.GET.get('required_resource_step', 0))
        except (ValueError, TypeError):
            current_idx = 0

        # Validação de limites
        if not required_resources or not (0 <= current_idx < total_resources):
            return {}

        parent = required_resources[current_idx]
        resources = ResourceSelectable.objects.filter(parent=parent).values(
            'id', 'name'
        )
        
        # Lógica de transição
        is_last_resource = (current_idx == total_resources - 1)
        
        return {
            'resources': list(resources),
            'parent': parent,
            'next_step': '3' if is_last_resource else '2',
            'next_resource_step': (current_idx + 1) % total_resources
        }

from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, UpdateAPIView

class AppConfigView(RetrieveAPIView,UpdateAPIView,APIView):
    queryset = AppConfig.objects.all()
    serializer_class = AppConfigSerializer
    permission_classes = [IsOwner]


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "pages/register/index.html"
    success_url = reverse_lazy('login')


class HomeView(LoginRequiredMixin,View):
    def get(self, request):
        from django.shortcuts import redirect
        if IsOnlyClient().has_permission(request, None):
            return redirect('self_scheduling')
        return redirect('app-schedule')
