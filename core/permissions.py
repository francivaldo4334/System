from rest_framework import permissions

class FullModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='OWNER').exists()

class IsFrontDesk(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='FRONT_DESK').exists()

class IsProfessional(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='PROFESSIONAL').exists()

class IsOnlyClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return all([
                not C().has_permission(request, view) for C in
                [
                    IsOwner,
                    IsFrontDesk,
                    IsProfessional,
                ]
            ])
