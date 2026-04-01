from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from app.forms import AvailabilityForm
from app.tables import Header, HeaderOption, RowData, Table


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
    # template_name="pages/app/schedule/settings/availabilities/index.html"
    template_name="layouts/crud/index.html"
    extra_context={
        "key": "availabilities",
        "create": {
            "form": AvailabilityForm,
        },
        "list": {
            "table": Table(
                list_url_name="availabilities-list",
                header=Header(
                    options=[
                        HeaderOption(
                            label=_("Description")
                        )
                    ]
                ),
                row_data=RowData(
                    key="",
                    type="",
                )
            ),
        }
    }
