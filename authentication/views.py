from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
