from django.shortcuts import render

# Create your views here.
def app_view(r):
    return render(r, 'app.html')
