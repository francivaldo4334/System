from django.urls import path

from app.views import AppScheduleView, AppView

urlpatterns = [
    path('', AppView.as_view(), name="app"),
    path('', AppScheduleView.as_view(), name='schedule_view'),
]
