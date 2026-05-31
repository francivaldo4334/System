import os
from django.contrib.auth import get_user_model
from django.contrib.auth.views import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.services import SendEmail
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta

from schedule.models import Assignment, Availability

User = get_user_model()

# Create your views here.
@login_required
def waiting_email_confirmation(request):
    print(request.user and hasattr(request.user, 'is_email_checked') and request.user.is_email_checked)
    if request.user and hasattr(request.user, 'is_email_checked') and request.user.is_email_checked:
        return redirect('/')
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
        print(request.user and hasattr(request.user, 'is_email_checked') and request.user.is_email_checked)
        if request.user and hasattr(request.user, 'is_email_checked') and request.user.is_email_checked:
            redirect('/')
        try:
            # RECOMENDAÇÃO: Disparar isso como uma task assíncrona (ex: Celery)
            # send_email_confirmation_task.delay(request.user.id)
            SendEmail().send_email_cofirmation(request.user, request)
            
            return Response(
                {"detail": _("Confirmation email sent successfully.")}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": _("We were unable to send the email at this time. Please try again later.")},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @action(
        methods=["GET"], 
        detail=False, 
        url_path=r'active_account/(?P<uuid>[^/.]+)/(?P<token>[^/.]+)', 
        url_name='active-account',
        permission_classes=[AllowAny]
    )
    def active_account(self, request, uuid, token):
        user = get_object_or_404(User, uid=uuid)
        if default_token_generator.check_token(user, token):
            user.is_email_checked = True # Certifique-se de que este campo existe no seu User customizado
            user.save()
            return Response({"detail": "Success"}, status=status.HTTP_200_OK)
        return Response({"detail": "Error"}, status=status.HTTP_400_BAD_REQUEST)            

    def handle_exception(self, exc):
        try:
            return super().handle_exception(exc)
        except ValidationError as e:
            return Response(e.message,400)


@method_decorator(csrf_exempt, name='dispatch')
class TriggerClientRemindersAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        # 1. Proteção por Token
        auth_token = request.headers.get('Authorization')
        expected_token = os.environ.get('CRON_SECRET_TOKEN', 'token-super-seguro-local')
        
        if auth_token != f"Bearer {expected_token}":
            return Response("Não autorizado.", status.HTTP_401_UNAUTHORIZED)

        notifier = SendEmail()
        today = timezone.now().date()
        tomorow = today + timedelta(days=1)
        
        # =========================================================================
        # PARTE 1: PROCESSAR AGENDAMENTOS DOS CLIENTES (1 e 3 dias de antecedência)
        # =========================================================================
        prazos_agendamentos = [1, 3]
        
        for dias in prazos_agendamentos:
            data_alvo = today + timedelta(days=dias)
            
            # Filtra agendamentos ativos na data alvo usando seu manager customizado.
            # Adicionalmente, limitamos a estados que fazem sentido receber lembrete.
            assignments = Assignment.objects.visibles().filter(
                date=data_alvo,
                status__in=[Assignment.Status.PENDING.value, Assignment.Status.CONFIRMED.value]
            ).prefetch_related('resources__parent')
            
            for assignment in assignments:
                notifier.send_email_reminder(assignment=assignment, days_remaining=dias)

        # =========================================================================
        # PARTE 2: PROCESSAR GERENTES COM DISPONIBILIDADE EXPIRANDO (Falta 1 dia)
        # =========================================================================
        # Busca grades de horários que vencem exatamente amanhã
        availabilities_expirando = Availability.objects.filter(valid_until=tomorow)
        
        if availabilities_expirando.exists():
            # Para evitar enviar múltiplos e-mails para o mesmo gerente caso ele tenha 
            # mais de uma grade expirando amanhã, buscamos os gerentes do sistema.
            # (Ajuste o filtro de grupos/permissões conforme seu banco)
            managers = User.objects.filter(is_active=True, groups__name="OWNER")
            
            for manager in managers:
                notifier.send_email_manager_reminder(manager_user=manager)

        return Response({
            "status": "success", 
            "message": "Processamento de lembretes de clientes e gerentes concluído."
        })
# import os
# import urllib.request

# def lambda_handler(event, context):
#     url = "https://seu-sistema.com/api/cron/send-client-reminders/"
#     token = os.environ.get('CRON_SECRET_TOKEN')
    
#     req = urllib.request.Request(
#         url, 
#         method="POST", 
#         headers={"Authorization": f"Bearer {token}"}
#     )
    
#     try:
#         with urllib.request.urlopen(req) as response:
#             return {"statusCode": 200, "body": "Django API triggered successfully"}
#     except Exception as e:
#         print(f"Error triggering Django API: {e}")
#         raise e
