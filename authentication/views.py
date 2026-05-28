from django.contrib.auth import get_user_model
from django.contrib.auth.views import default_token_generator
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.services import SendEmail
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny

User = get_user_model()

# Create your views here.
@login_required
def waiting_email_confirmation(request):
    def mask_email(email):
        try:
            email_parts = email.split('@')
            masked_name = email_parts[0][:2] + "*" * (len(email_parts[0]) - 2)
            return f"{masked_name}@{email_parts[1]}"
        except Exception:
            return "sua conta"
    return render(request,'pages/waiting_email_confirmation/index.html',
      {
          'email_preview': mask_email(request.user.email)
      }
    )
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

# Criação de um Throttle específico para evitar spam de e-mail
class EmailResendThrottle(UserRateThrottle):
    rate = '2/minute'  # Permite apenas 2 envios por minuto por usuário


class EmailViewSet(viewsets.ViewSet):
    # Throttle padrão mapeado para a Action
    throttle_classes = [] 

    def get_permissions(self):
        """
        Garante que a permissão seja aplicada corretamente 
        apenas na action de confirmação de e-mail.
        """
        if self.action == 'email_confirmation':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["POST"], throttle_classes=[EmailResendThrottle])
    def email_confirmation(self, request):
        try:
            # RECOMENDAÇÃO: Disparar isso como uma task assíncrona (ex: Celery)
            # send_email_confirmation_task.delay(request.user.id)
            SendEmail().send_email_cofirmation(request.user, request)
            
            return Response(
                {"detail": _("Confirmation email sent successfully.")}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Tratamento defensivo caso o provedor de e-mail falhe
            return Response(
                {"detail": "We were unable to send the email at this time. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @action(["POST"], False, 'active_account/<str:uuid>/<str:token>', permission_classes=[AllowAny])
    def active_account(self, request, uuid, token):
        user = get_object_or_404(User, id=uuid)
        if default_token_generator.check_token(user, token):
            user.is_email_checked = True
            user.save()
            return Response({"detail": "Success"})
        return Response({"detail": "Error"}, 400)
            

