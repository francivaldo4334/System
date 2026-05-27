from django.shortcuts import render

# Create your views here.
def waiting_email_confirmation(request):
    return render(request,'pages/waiting_email_confirmation/index.html')
