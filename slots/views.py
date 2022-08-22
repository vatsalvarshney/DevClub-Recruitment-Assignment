from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Sport

def dashboardRedirect(request):
    return redirect(reverse('dashboard'))

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'slots/dashboard.html', {'sports': Sport.objects.all()})
