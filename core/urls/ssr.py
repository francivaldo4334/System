from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, reverse
from django.conf.urls.i18n import i18n_patterns

from core.views import LandingPageView

def redirec_to_app(request):
    if not request.tenant.is_master:
        return redirect(reverse('app'))
    return redirect('admin:index')
    # def _view(request,*args, **kwargs):
        # return redirect(reverse('app'))
    #         return view(request,*args, **kwargs)
    # return _view

# def to_app_page(request):
#     if hasattr(request.user, 'is_email_checked') and request.user.is_email_checked:
#         return redirect('/app/')
#     return redirect(reverse('waiting_email_confirmation'))


urlpatterns = i18n_patterns(
    path('',redirec_to_app),
    path('admin/', admin.site.urls),
    # path('', to_app_page),
    path('app/', include('app.urls')),
    path('', include('authentication.urls')),
    path('app/schedule/', include('schedule.urls')),
)
