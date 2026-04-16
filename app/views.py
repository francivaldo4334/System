from typing import Type
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from app.forms import AssignmentForm, AvailabilityForm, BaseForm, ResourceForm, ServiceForm, ServiceRequirementsForm
from app.tables import AvailabilityTable, BaseTable, ResourcesTable, ServiceRequirementsTable, ServicesTable, Table


class AppView(LoginRequiredMixin,TemplateView):
    template_name = "pages/app/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app_template_name_options': [
                {
                    'url_name': 'app-schedule',
                    'title': _('Agenda'),
                    'icon_template_name': 'icons/calendar.svg'
                },
                {
                    'url_name': 'app-schedule-settings',
                    'title': _('Agenda Settings'),
                    'icon_template_name': 'icons/calendar-cog.svg'
                },
            ],
            'today': f'{timezone.localtime(timezone.now()).date().isoformat()}T00:00:00',
        })
        return context
    def get_template_names(self):
        if self.request.META.get('HTTP_AJAX_REQUEST', False):
            self.template_name += "#main"
        return super().get_template_names()

class AppScheduleView(AppView):
    template_name = 'pages/app/schedule/index.html'
    extra_context = {
        'assignment_form': AssignmentForm
    }

class AppScheduleSettingsView(AppView):
    template_name = 'pages/app/schedule/settings/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'setting_tag_selected': 'app-schedule-settings-availabilities',
            'setting_tabs': [
                {
                    'label': _("Availabilities"),
                    'url_name': 'app-schedule-settings-availabilities',
                },
                {
                    'label': _("Resources"),
                    'url_name': 'app-schedule-settings-resources',
                },
                {
                    'label': _("Services"),
                    'url_name': 'app-schedule-settings-services',
                },
                {
                    'label': _("Service Requirements"),
                    'url_name': 'app-schedule-settings-service-requirements',
                },
            ]
        })
        return context

class CrudView(LoginRequiredMixin, TemplateView):
    template_name = 'layouts/crud/index.html'
    key: str
    form: Type[BaseForm]
    table: Type[BaseTable]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form_instance = self.form()
        
        context.update({
            'key': self.key,
            'create': {
                'form': form_instance,
                'post_url_name': f'{self.key}-list',
            },
            'list': {
                'table': self.table,
            },
            'delete': {
                'delete_url_name': f'{self.key}-detail',
            },
            'update': {
                'form': form_instance,
                'update_url_name': f'{self.key}-detail'
            },
        })
        return context

class ScheduleSettingsAvailabilitiesView(CrudView):
    key = 'availabilities'
    form = AvailabilityForm
    table = AvailabilityTable

class ScheduleSettingsResourceView(CrudView):
    key = 'resources'
    form = ResourceForm
    table = ResourcesTable

class ScheduleSettingsServiceView(CrudView):
    key = 'services'
    form = ServiceForm
    table = ServicesTable

class ScheduleSettingsServiceRequirementsView(CrudView):
    key = 'service_requirements'
    form = ServiceRequirementsForm
    table = ServiceRequirementsTable
