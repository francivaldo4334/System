from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, reverse
from django.conf.urls.i18n import i18n_patterns

def to_app_page(request):
    if hasattr(request.user, 'is_email_checked') and request.user.is_email_checked:
        return redirect('/app/')
    return redirect(reverse('waiting_email_confirmation'))


urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', to_app_page),
    path('app/', include('app.urls')),
    path('', include('authentication.urls')),
    path('app/schedule/', include('schedule.urls')),
)
