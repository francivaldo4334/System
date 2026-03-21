from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.i18n import i18n_patterns

def to_app_page(request):
    return redirect('/app/')

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', to_app_page),
    path('app/', include('app.urls')),
    path('app/schedule/', include('schedule.urls')),
)
