from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from users.models import Role
from .models import Sport, Arena, Slot
from .forms import ConfirmationForm, SportForm, ArenaForm, SlotCreationFormNoRepeat, SlotCreationFormDaily, SlotCreationFormWeekly
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


@login_required(login_url='login')
def context(request, sport_id=None, arena_id=None):
    c= {
        'ismemeber': request.user.role.contains(Role.objects.get(id=3)),
        'isstaff': request.user.role.contains(Role.objects.get(id=2)),
        'isadmin': request.user.role.contains(Role.objects.get(id=1))
    }
    if sport_id:
        c['sport']=Sport.objects.get(id=sport_id)
    if arena_id:
        c['arena']=Arena.objects.get(id=arena_id)
    return c


def dashboardRedirect(request):
    return redirect(reverse('dashboard'))

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'slots/dashboard.html', {'sports': Sport.objects.all()})


def sportHome(request, sport_id):
    cont=context(request, sport_id)
    cont['arenas']=cont['sport'].arena_set.all()
    return render(request, 'slots/sport-home.html', cont)

def sportCreate(request):
    cont=context(request)
    if request.method == 'POST':
        form = SportForm(request.POST)
        if form.is_valid():
            sport=form.save()
            messages.success(request, f'Sport {sport} has been created!')
            return redirect(reverse('sport-home', args=[sport.id]))
    else:
        form = SportForm()
    cont['form']= form
    return render(request, 'slots/sport-create.html', cont)

def sportEdit(request, sport_id):
    cont=context(request, sport_id)
    if request.method == 'POST':
        form = SportForm(request.POST, instance=cont['sport'])
        if form.is_valid():
            form.save()
            messages.success(request, f'Sport {cont["sport"]} has been updated!')
            return redirect(reverse('sport-home', args=[sport_id]))
    else:
        form = SportForm(instance=cont['sport'])
    cont['form']=form
    return render(request, 'slots/sport-edit.html', cont)

def sportDelete(request, sport_id):
    cont=context(request, sport_id)
    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            n=cont['sport'].name
            cont['sport'].delete()
            messages.success(request, f'Sport "{n}" has been deleted successfully')
            return redirect('dashboard')
    else:
        form = ConfirmationForm()
    cont['form']=form
    return render(request, 'slots/sport-delete.html', cont)


def arenaHome(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    cont['slots']=cont['arena'].slot_set.all()
    return render(request, 'slots/arena-home.html', cont)

def arenaCreate(request, sport_id):
    cont=context(request, sport_id)
    if request.method == 'POST':
        form = ArenaForm(request.POST, initial={'sport': cont['sport']})
        if form.is_valid():
            arena=form.save()
            messages.success(request, f'Arena {arena} has been created!')
            return redirect(reverse('arena-home', args=[sport_id, arena.id]))
    else:
        form = ArenaForm(initial={'sport': cont['sport']})
    cont['form']= form
    return render(request, 'slots/arena-create.html', cont)

def arenaEdit(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if request.method == 'POST':
        form = ArenaForm(request.POST, instance=cont['arena'])
        if form.is_valid():
            form.save()
            messages.success(request, f'Arena {cont["arena"]} has been updated!')
            return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    else:
        form = ArenaForm(instance=cont['arena'])
    cont['form']=form
    return render(request, 'slots/arena-edit.html', cont)

def arenaDelete(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            n=cont['arena'].name
            cont['arena'].delete()
            messages.success(request, f'Arena "{n}" has been deleted successfully')
            return redirect(reverse('sport-home', args=[sport_id]))
    else:
        form = ConfirmationForm()
    cont['form']=form
    return render(request, 'slots/arena-delete.html', cont)


def slotCreateNoRepeat(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if request.method == 'POST':
        form = SlotCreationFormNoRepeat(request.POST, initial={'arena':cont['arena']})
        if form.is_valid():
            arena=Arena.objects.get(id=request.POST.get('arena'))
            if form.cleaned_data.get('start_time')>=form.cleaned_data.get('end_time'):
                messages.error(request, 'End time should be after start time')
            elif form.cleaned_data.get('current_player_capacity')>arena.max_player_capacity:
                messages.error(request, "Player capacity can't be more than max player capacity of the arena")
            elif form.cleaned_data.get('current_spectator_capacity')>arena.max_spectator_capacity:
                messages.error(request, "Spectator capacity can't be more than max spectator capacity of the arena")
            else:
                slot=form.save()
                messages.success(request, f'Slot {slot} has been created!')
                return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    else:
        form = SlotCreationFormNoRepeat(initial={'arena':cont['arena']})
    cont['form']= form
    return render(request, 'slots/slot-create.html', cont)

def slotCreateDaily(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if request.method == 'POST':
        form = SlotCreationFormDaily(request.POST, initial={'arena':cont['arena']})
        if form.is_valid():
            arena=Arena.objects.get(id=request.POST.get('arena'))
            st=datetime.strptime(request.POST.get('starting_time'), '%H:%M').time()
            et=datetime.strptime(request.POST.get('ending_time'), '%H:%M').time()
            sd=datetime.strptime(request.POST.get('repeat_daily_starting_from_date'), '%Y-%m-%d').date()
            ed=datetime.strptime(request.POST.get('repeat_daily_until_date'), '%Y-%m-%d').date()
            if st>=et:
                messages.error(request, 'End time should be after start time')
            elif sd>ed:
                messages.error(request, 'End date should be after start date')
            elif request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_player_capacity'))>arena.max_player_capacity:
                    messages.error(request, "Player capacity can't be more than max player capacity of the arena")
            elif request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_spectator_capacity'))>arena.max_spectator_capacity:
                    messages.error(request, "Spectator capacity can't be more than max spectator capacity of the arena")
            else:
                dt=sd
                while dt<=ed:
                    slot=Slot(
                        name=request.POST.get('name'),
                        arena=arena,
                        start_time=make_aware(datetime.combine(dt,st)),
                        end_time=make_aware(datetime.combine(dt,et)),
                        current_player_capacity=request.POST.get('current_player_capacity'),
                        current_spectator_capacity=request.POST.get('current_spectator_capacity'),
                    )
                    slot.save()
                    dt=dt+timedelta(days=1)
                messages.success(request, 'Slots have been created!')
                return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    else:
        form = SlotCreationFormDaily(initial={'arena':cont['arena']})
    cont['form']= form
    return render(request, 'slots/slot-create.html', cont)

def slotCreateWeekly(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if request.method == 'POST':
        form = SlotCreationFormWeekly(request.POST, initial={'arena':cont['arena']})
        if form.is_valid():
            arena=Arena.objects.get(id=request.POST.get('arena'))
            st=datetime.strptime(request.POST.get('starting_time'), '%H:%M').time()
            et=datetime.strptime(request.POST.get('ending_time'), '%H:%M').time()
            sd=datetime.strptime(request.POST.get('repeat_weekly_starting_from_date'), '%Y-%m-%d').date()
            ed=datetime.strptime(request.POST.get('repeat_weekly_until_date'), '%Y-%m-%d').date()
            days_list=form.cleaned_data.get('repeating_days')
            if st>=et:
                messages.error(request, 'End time should be after start time')
            elif sd>ed:
                messages.error(request, 'End date should be after start date')
            elif request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_player_capacity'))>arena.max_player_capacity:
                    messages.error(request, "Player capacity can't be more than max player capacity of the arena")
            elif request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_spectator_capacity'))>arena.max_spectator_capacity:
                    messages.error(request, "Spectator capacity can't be more than max spectator capacity of the arena")
            else:
                for day in days_list:
                    initial_offset=(int(day)-sd.weekday())%7
                    dt=sd+timedelta(days=initial_offset)
                    while dt<=ed:
                        slot=Slot(
                            name=request.POST.get('name'),
                            arena=arena,
                            start_time=make_aware(datetime.combine(dt,st)),
                            end_time=make_aware(datetime.combine(dt,et)),
                            current_player_capacity=request.POST.get('current_player_capacity'),
                            current_spectator_capacity=request.POST.get('current_spectator_capacity'),
                        )
                        slot.save()
                        dt=dt+timedelta(days=7)
                messages.success(request, 'Slots have been created!')
                return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    else:
        form = SlotCreationFormWeekly(initial={'arena':cont['arena']})
    cont['form']= form
    return render(request, 'slots/slot-create.html', cont)
