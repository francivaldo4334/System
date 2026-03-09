from django.urls import path

from app.views import app_view, ui_view

urlpatterns = [
    path('', app_view, name="app"),
    path('ui/', ui_view, name="ui"),
    
]
