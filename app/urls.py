from django.urls import path
from app.views import (
    AppConfigView, AppConfitView, AppScheduleSettingsView, AppScheduleView, HomeView,
    ScheduleSettingsAvailabilitiesView, ScheduleSettingsResourceCategoryView, ScheduleSettingsResourcePersonView,
    ScheduleSettingsResourceView, ScheduleSettingsServiceRequirementsView,
    ScheduleSettingsServiceView, ScheduleSettingsTimeBlockView, SelfScheduleView, RegisterView, SettingsUserView,
)
from django.contrib.auth import views as auth_views

from core.views import is_not_tenant_master

urlpatterns = [
    path('', HomeView.as_view(), name="app"),
    path('schedule', AppScheduleView.as_view(), name='app-schedule'),
    path('schedule/settings', AppScheduleSettingsView.as_view(), name='app-schedule-settings'),
    path('schedule/settings/availabilities', ScheduleSettingsAvailabilitiesView.as_view(), name="app-schedule-settings-availabilities"),
    path('schedule/settings/time_block', ScheduleSettingsTimeBlockView.as_view(),name="app-schedule-settings-time-block"),
    path('schedule/settings/resources_category', ScheduleSettingsResourceCategoryView.as_view(), name='app-schedule-settings-resources_category'),
    
    # NOVAS ROTAS DINÂMICAS: Sem queries no startup, capturando a key direto da URL
    path('schedule/settings/resource/object/<str:key>/', ScheduleSettingsResourceView.as_view(), name='app-schedule-settings-resource-object'),
    path('schedule/settings/resource/person/<str:key>/', ScheduleSettingsResourcePersonView.as_view(), name='app-schedule-settings-resource-person'),
    
    path('schedule/settings/services', ScheduleSettingsServiceView.as_view(), name="app-schedule-settings-services"),
    path('schedule/settings/users', SettingsUserView.as_view(), name="app-schedule-settings-users"),
    path("schedule/settings/config", AppConfitView.as_view(), name="app-schedule-settings-config"),
    # path('schedule/settings/service_requirements', ScheduleSettingsServiceRequirementsView.as_view(), name="app-schedule-settings-service-requirements"),
    path('self-scheduling', SelfScheduleView.as_view(), name="self_scheduling"),
    path('login/',
         is_not_tenant_master(
             auth_views.LoginView.as_view(template_name="pages/login/index.html")
         ),
          name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('register/',
          is_not_tenant_master(RegisterView.as_view()),
          name="register"),
    path('api/config', AppConfigView.as_view(), name="app-config")
]
