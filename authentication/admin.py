from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication.models import CustomUser
from django.utils.translation import gettext_lazy as _

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password", 'uid')}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "whatsapp_phone")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    'is_email_checked',
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
