from rest_framework.permissions import BasePermission

class IsEmailCheckedPermission(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user,'is_email_checked') and request.user.is_email_checked
