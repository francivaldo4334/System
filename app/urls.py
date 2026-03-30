from django.urls import include, path

from app.views import AppScheduleSettingsView, AppScheduleView, AppView, ScheduleSettingsAvailabilitiesView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', AppView.as_view(),{'default_url_name': 'app-schedule'},name="app"),
    path('schedule', AppScheduleView.as_view(), name='app-schedule'),
    path('schedule/settings', AppScheduleSettingsView.as_view(), name='app-schedule-settings'),
    path('schedule/settings/availabilities',ScheduleSettingsAvailabilitiesView.as_view(), name="app-schedule-settings-availabilities"),
    path('login/', auth_views.LoginView.as_view(template_name="pages/login/index.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
]
