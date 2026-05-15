from django.shortcuts import render

def alerts(request):
    return render(request, 'alerts/alerts.html')