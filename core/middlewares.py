from django.shortcuts import redirect
from django.urls import reverse

class MasterAdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se o tenant existe e se é master
        if hasattr(request, 'tenant') and request.tenant.is_master:
            
            # Define o path do admin (ajuste se seu admin tiver prefixo diferente)
            admin_path = reverse('admin:index') 
            
            # Se o usuário não estiver no admin, bloqueia o acesso
            # Verifica se o path atual não começa com o path do admin
            if not request.path.startswith(admin_path):
                # Redireciona para o admin ou levanta PermissionDenied
                return redirect('admin:index')

        return self.get_response(request)
