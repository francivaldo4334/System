from django.contrib import admin

# Register your models here.
from django_tenants.admin import TenantAdminMixin

from customer.models import Client

@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
        list_display = ('name', 'paid_until')
