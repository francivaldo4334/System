import os
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

from schedule.utils import slot_to_time

class SendEmail:
    def send_email_ticket(self, assignment, request, user):
        start_time = slot_to_time(assignment.start_slot)
        end_slot = assignment.start_slot + assignment.duration_slot
        end_time = slot_to_time(end_slot)

        time_range = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        resources = ", ".join([r.name for r in assignment.resources.all()])

        domain = request.get_host()
        path = reverse('assignment-ticker-download', kwargs={'pk': assignment.pk})
        protocol = 'https' if request.is_secure() else 'http'
        download_link = f"{protocol}://{domain}{path}"
        from_email = os.environ.get('EMAIL_HOST_USER', 'no-reply@seu-dominio.com')

        # Contexto enviado para o HTML (passamos apenas as variáveis puras,
        # a tradução dos rótulos/textos fixos deve ocorrer dentro do próprio template)
        template_context = {
            'assignment': assignment,
            'dynamic_time_range': time_range,
            'resource_names': resources,
            'download_link': download_link,
            'user': user,
        }

        # 1. Assunto do E-mail internacionalizado
        subject = _("Comprovante de Agendamento - Confirmação")

        # 2. Texto de Fallback (Puro) internacionalizado usando .format()
        message_txt = _(
            "Olá, {username}.\n\n"
            "Seu agendamento foi confirmado com sucesso!\n\n"
            "Detalhes do Agendamento:\n"
            " Horário: {time_range}\n"
            " Recurso(s): {resources}\n\n"
            "Você pode baixar o seu comprovante em PDF acessando o link abaixo:\n"
            "{download_link}\n\n"
            "Obrigado!"
        ).format(
            username=user.username,
            time_range=time_range,
            resources=resources,
            download_link=download_link
        )

        html_message = render_to_string('emails/assignment_ticket/index.html', template_context)

        send_mail(
            subject=subject,
            message=message_txt,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_message
        )
        return True

    def send_email_cofirmation(self, user, request):
        uid = user.uid
        # 2. Gera o token seguro baseado no estado atual do usuário
        token = default_token_generator.make_token(user)
        
        # 3. Obtém o domínio atual da requisição
        domain = request.get_host()
        
        # 4. Resolve a URL dinamicamente pelo nome da rota usando reverse
        # Substitua 'ativar_conta' pelo nome exato (name=...) definido no seu urls.py
        path = reverse('send_email-active-account', kwargs={'uuid': str(uid), 'token': token})
        
        # 5. Monta o link absoluto (identifica automaticamente se é http ou https)
        protocol = 'https' if request.is_secure() else 'http'
        confirmation_link = f"{protocol}://{domain}{path}"
        
        # 6. Captura o e-mail do remetente das variáveis de ambiente (com fallback de segurança)
        from_email = os.environ.get('EMAIL_HOST_USER', 'no-reply@seu-dominio.com')
        
        # 7. Renderiza um template HTML opcional (Altamente recomendável para e-mails profissionais)
        context = {
            'user': user, 
            'confirmation_link': confirmation_link
        }
        html_message = render_to_string('emails/confirm_email/index.html', context)

        
        # Texto simples de fallback caso o cliente de e-mail não suporte HTML
        message_txt = _(
            "Hello, {username}.\n\nPlease confirm your registration by clicking the link below:\n{link}"
        ).format(username=user.username, link=confirmation_link)
        
        # 8. Dispara o e-mail
        send_mail(
            subject=_("Registration Confirmation"),
            message=message_txt,
            from_email=from_email,
            recipient_list=[user.email],
            # fail_silently=False,  # Altere para True em produção se não quiser que a app trave caso o servidor de e-mail caia
            html_message=html_message
        )
        
        return True
