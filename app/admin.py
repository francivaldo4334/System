from django.contrib import admin

from app.models import AppConfig, ResourceSlugVisible

# Register your models here.
@admin.register(AppConfig)
class AppConfigAdmin(admin.ModelAdmin):
    pass

@admin.register(ResourceSlugVisible)
class ResourceSlugVisibleAdmin(admin.ModelAdmin):
    pass
