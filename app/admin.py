from django.contrib import admin

from app.models import AppConfig

# Register your models here.
@admin.register(AppConfig)
class AppConfigAdmin(admin.ModelAdmin):
    pass
