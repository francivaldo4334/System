from django.shortcuts import render

# Create your views here.
def app_view(r):
    return render(r, 'pages/app/index.html')

def schedule_view(request):
    return render(request, 'schedule.html')
