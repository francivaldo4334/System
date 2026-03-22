from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class AppView(TemplateView):
    template_name="pages/app/index.html"
    extra_context = {
        
    }

class AppScheduleView(AppView):
    template_name = 'schedule.html'
