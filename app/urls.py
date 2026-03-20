from django.urls import path

from app.views import app_view, schedule_view

urlpatterns = [
    path('', app_view, name="app"),
    path('', schedule_view, name='schedule_view'),
]
