from django.urls import path

from app.views import (
    AppConfigView,
    AppScheduleSettingsView,
    AppScheduleView,
    HomeView,
    ScheduleSettingsAvailabilitiesView,
    ScheduleSettingsResourcePersonView,
    ScheduleSettingsResourceView,
    ScheduleSettingsServiceRequirementsView,
    ScheduleSettingsServiceView,
    SelfScheduleView,
    RegisterView,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', HomeView.as_view(),name="app"),
    path('schedule', AppScheduleView.as_view(), name='app-schedule'),
    path('schedule/settings', AppScheduleSettingsView.as_view(), name='app-schedule-settings'),
    path('schedule/settings/availabilities',ScheduleSettingsAvailabilitiesView.as_view(), name="app-schedule-settings-availabilities"),
    #path('schedule/settings/resources',ScheduleSettingsResourceView.as_view(), name="app-schedule-settings-resources"),
    *[
        path(
            f'schedule/settings/resource/{it}/',
            ScheduleSettingsResourceView.as_view(key=it),
            name=f'app-schedule-settings-resource-{it}'
        ) for it in ScheduleSettingsResourceView.get_options() + ScheduleSettingsResourcePersonView.get_options()
    ],
    path('schedule/settings/services',ScheduleSettingsServiceView.as_view(), name="app-schedule-settings-services"),
    path('schedule/settings/service_requirements',ScheduleSettingsServiceRequirementsView.as_view(), name="app-schedule-settings-service-requirements"),
    path('self-scheduling', SelfScheduleView.as_view(), name="self_scheduling"),
    path('login/', auth_views.LoginView.as_view(template_name="pages/login/index.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="register"),
    # app api/
    path('api/config', AppConfigView.as_view(), name="app-config")
]
