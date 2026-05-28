from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

class SendEmail:
    def send_email_cofirmation(self, user, request):
        uid = user.id
        token = default_token_generator.make_token(user)
        domain = request.get_host()
        confirmation_link = ''
        # send_mail(
        #     subject="",
        #     message=""
        #     from_email=None,
        #     recipient_list=[user.email],
        #     html_message=
        # )
        return
