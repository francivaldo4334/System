from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def to_app_page(request):
    return redirect('/app/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', to_app_page),
    path('app/', include('app.urls')),
    path('app/schedule/', include('schedule.urls')),
]
