from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your views here.
class AppView(TemplateView):
    template_name="pages/app/index.html"
    extra_context = {
      'app_template_name_options': [
          {
              'url_name': 'app-schedule',
              'title': _('Agenda'),
              'icon_template_name': 'icons/calendar.svg'
          }
      ],
      'default_app_template_name': 'pages/app/schedule/index.html#main',
      'today': f'{timezone.localtime(timezone.now()).date().isoformat()}T00:00:00',
    }

class AppScheduleView(AppView):
    template_name = 'pages/app/schedule/index.html'
