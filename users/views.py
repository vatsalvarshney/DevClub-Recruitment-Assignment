from django.shortcuts import render, redirect
from .forms import UserRegisterForm, PfpChangeForm
from .models import User, Role
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            user=User.objects.get(username=username)
            user.role.add(Role.objects.get(id=3))
            user.save()
            messages.success(request, f'Your account has been created! Log in to continue')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required(login_url='login')
def profile(request, username):
    if User.objects.filter(username=username):
        view_user=User.objects.get(username=username)
        if view_user.is_active:
            return render(request, 'users/profile.html', {'view_user': view_user})
        else:
            return render(request, 'users/no-profile.html', {'exists': True})
    else:
        return render(request, 'users/no-profile.html', {'exists': False})

@login_required(login_url='login')
def pwdChange(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your password has been updated! Log in to continue')
            return redirect('login')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/pwd-change.html', {'form': form})


@login_required(login_url='login')
def pfpChange(request):
    if request.method == 'POST':
        form = PfpChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your profile picture has been updated!')
            return redirect(reverse('profile', args=[request.user.username]))
    else:
        form = PfpChangeForm(instance=request.user)
    return render(request, 'users/pfp-change.html', {'form': form})

