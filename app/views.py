from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


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
                }
            ]
        })
        return context

class ScheduleSettingsAvailabilitiesView(LoginRequiredMixin, TemplateView):
    template_name="pages/app/schedule/settings/availabilities/index.html"
    extra_context={
        "key": "availabilities",
        "form_fields": [
            {
                "type": "select",
                "id": "id_resource_type",
                "label": _("Resource Type"),
                "name": "resource_type",
                "attrs": "required",
                "url_name": "resources",
            },
            {
                "type": "select",
                "id": "id_resource",
                "label": _("Resource"),
                "name": "resource",
                "attrs": "required disabled",
            },
            {
                "type": "date",
                "id": "id_valid_from",
                "label": _("Valid From"),
                "name": "valid_from",
                "attrs": 'required type="date"',
            },
            {
                "type": "date",
                "id": "id_valid_until",
                "label": _("Valid Until"),
                "name": "valid_until",
                "attrs": 'required type="date"',
            },
            {
                "type": "checkboxes",
                "id": "id_week",
                "label": _("Weekdays"),
                "name": "week",
                'options': [
                    { "value": '1', "label": _("Mon"), "attrs": "checked"},
                    { "value": '2', "label": _("Tue"), "attrs": "checked" },
                    { "value": '3', "label": _("Wed"), "attrs": "checked" },
                    { "value": '4', "label": _("Thu"), "attrs": "checked" },
                    { "value": '5', "label": _("Fri"), "attrs": "checked" },
                    { "value": '6', "label": _("Sat") },
                    { "value": '7', "label": _("Sun") },
                ]
            },
            {
                "type": "time",
                "id": "id_start_time",
                "label": _("Start Time"),
                "name": "start_time",
                "attrs": 'required',
                "step": "300",
            },
            {
                "type": "time",
                "id": "id_end_time",
                "label": _("End Time"),
                "name": "end_time",
                "attrs": 'required',
                "step": "300",
            },

            {
                "type": "time",
                "id": "id_duration",
                "label": _("Duration"),
                "name": "duration",
                "attrs": 'required',
                "step": "300",
            },
            {
                "type": "time",
                "id": "id_interval",
                "label": _("Interval"),
                "name": "interval",
                "attrs": 'required',
                "step": "300",
            },
            {
                "type": "textaria",
                "id": "id_description",
                "label": _("Description"),
                "name": "description",
            },
        ]
    }
