from django.urls import path

from app.views import app_view

urlpatterns = [
    path('', app_view, name="app")
]
