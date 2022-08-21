from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from .models import User, Role
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            r = Role.objects.get(id=3)
            form.save()
            username=form.cleaned_data.get('username')
            user=User.objects.get(username=username)
            user.role.add(r)
            user.save()
            messages.success(request, f'Your account has been created! Log in to continue')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
