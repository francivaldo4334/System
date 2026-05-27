from rest_framework.permissions import BasePermission

class IsEmailCheckedPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_email_checked
