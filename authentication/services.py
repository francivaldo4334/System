import os
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

class SendEmail:
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
        message_txt = f"Olá, {user.username}.\n\nPor favor, confirme seu cadastro clicando no link abaixo:\n{confirmation_link}"
        
        # 8. Dispara o e-mail
        send_mail(
            subject="Confirmação de Cadastro",
            message=message_txt,
            from_email=from_email,
            recipient_list=[user.email],
            # fail_silently=False,  # Altere para True em produção se não quiser que a app trave caso o servidor de e-mail caia
            html_message=html_message
        )
        
        return True
