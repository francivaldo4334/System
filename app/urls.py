from django.urls import path

from app.views import AppScheduleView, AppView

urlpatterns = [
    path('', AppView.as_view(),{'default_url_name': 'app-schedule'}, name="app"),
    path('schedule', AppScheduleView.as_view(), name='app-schedule'),
]
