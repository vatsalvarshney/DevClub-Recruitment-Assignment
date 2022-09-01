from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from users.models import Role, User
from .models import Sport, Arena, Slot, Booking, RATING_PARAMETERS_LIST, RatingParameter, SportRating
from .forms import ConfirmationForm, SportForm, ArenaForm, SlotCreationFormNoRepeat, SlotCreationFormDaily, SlotCreationFormWeekly, SportRatingCreationForm
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.views.generic.list import ListView
import statistics


@login_required(login_url='login')
def context(request, sport_id=None, arena_id=None, slot_id=None):
    c= {
        'ismember': request.user.role.contains(Role.objects.get(id=3)),
        'isstaff': request.user.role.contains(Role.objects.get(id=2)),
        'isadmin': request.user.role.contains(Role.objects.get(id=1))
    }
    if sport_id:
        c['sport']=Sport.objects.get(id=sport_id)
    if arena_id:
        c['arena']=Arena.objects.get(id=arena_id)
    if slot_id:
        c['slot']=Slot.objects.get(id=slot_id)
    return c


def dashboardRedirect(request):
    return redirect(reverse('dashboard'))

@login_required(login_url='login')
def dashboard(request):
    cont=context(request)
    if cont['ismember']:
        now=datetime.today()
        today=now.date()
        dt=today
        bookings_list=[]
        while dt<=today+timedelta(days=6):
            bookings_set=request.user.booking_set.filter(slot__start_time__date=dt, slot__start_time__gte=now, is_active=True)
            if dt==today:
                dt_str='Today'
            elif dt==today+timedelta(days=1):
                dt_str='Tomorrow'
            else:
                dt_str=dt.strftime('%a')+', '+dt.strftime('%d')+' '+dt.strftime('%b')
            if bookings_set:
                bookings_list.append(( dt_str , bookings_set ))
            dt+=timedelta(days=1)
        cont['bookings_by_date']=bookings_list
    cont['sports']=Sport.objects.all()
    return render(request, 'slots/dashboard.html', cont)


@login_required(login_url='login')
def sportHome(request, sport_id):
    cont=context(request, sport_id)
    cont['arenas']=cont['sport'].arena_set.all()
    user_rating=cont['sport'].sportrating_set.filter(member=request.user)
    if user_rating:
        cont['rated_by_user']=True
        cont['user_rating']=user_rating.first()
        cont['sport_ratings']=cont['sport'].sportrating_set.exclude(member=request.user).order_by('-rating_time')
    else:
        cont['rated_by_user']=False
        cont['sport_ratings']=cont['sport'].sportrating_set.all().order_by('-rating_time')
    cont['rating_count']=cont['sport'].sportrating_set.all().count()
    if cont['rating_count']:
        net_ratings=[]
        sport_net_rating_sum=0
        for par in RATING_PARAMETERS_LIST:
            par_rating=round(statistics.fmean(RatingParameter.objects.filter(parameter=par,rating_group__sport=cont['sport']).values_list('rating', flat=True)),2)
            net_ratings.append((par.replace('_',' ').capitalize(),par_rating))
            sport_net_rating_sum+=par_rating
        cont['net_ratings']=net_ratings
        cont['sport_net_rating']=round(sport_net_rating_sum/len(RATING_PARAMETERS_LIST),2)
    return render(request, 'slots/sport-home.html', cont)


@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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


@login_required(login_url='login')
def arenaHome(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if not cont['ismember']:
        return redirect(reverse('arena-all-slots', args=[sport_id, arena_id]))
    now=datetime.today()
    today=now.date()
    dt=today
    slots_list=[]
    disallowed_dates_list=[]
    while dt<=today+timedelta(days=6):
        slots_list.append((dt.strftime('%A'),dt.strftime('%d')+' '+dt.strftime('%b'),cont['arena'].slot_set.filter(start_time__date=dt, start_time__gte=now).order_by('start_time')))
        if request.user.booking_set.filter(slot__start_time__date=dt, is_active=True).count()>=3:
            disallowed_dates_list.append(dt)
        dt+=timedelta(days=1)
    cont['slots_by_date']=slots_list
    cont['disallowed_dates_list']=disallowed_dates_list
    return render(request, 'slots/arena-home.html', cont)

@login_required(login_url='login')
def arenaAllSlots(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if not (cont['isstaff'] or cont['isadmin']):
        return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    now=datetime.today()
    today=now.date()
    dt=today
    slots_list=[]
    while dt<=today+timedelta(days=365):
        slots_set=cont['arena'].slot_set.filter(start_time__date=dt, start_time__gte=now).order_by('start_time')
        if slots_set:
            slots_list.append((dt.strftime('%a')+', '+dt.strftime('%d')+'/'+dt.strftime('%m') , slots_set))
        dt+=timedelta(days=1)
    paginator = Paginator(slots_list, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    cont['page_obj']=page_obj
    return render(request, 'slots/arena-all-slots.html', cont)


@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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


@login_required(login_url='login')
def slotCreateNoRepeat(request, sport_id, arena_id):
    cont=context(request, sport_id, arena_id)
    if request.method == 'POST':
        form = SlotCreationFormNoRepeat(request.POST, initial={'arena':cont['arena']})
        if form.is_valid():
            arena=Arena.objects.get(id=request.POST.get('arena'))
            is_error=False
            if form.cleaned_data.get('start_time')>=form.cleaned_data.get('end_time'):
                messages.error(request, 'End time should be after start time')
                is_error=True
            if request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_player_capacity'))>arena.max_player_capacity:
                    messages.error(request, "Player capacity can't be more than max player capacity of the arena")
                    is_error=True
            if request.POST.get('current_spectator_capacity')!='':
                if int(request.POST.get('current_spectator_capacity'))>arena.max_spectator_capacity:
                    messages.error(request, "Spectator capacity can't be more than max spectator capacity of the arena")
                    is_error=True
            if not is_error:
                slot=form.save()
                messages.success(request, f'Slot {slot} has been created!')
                return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    else:
        form = SlotCreationFormNoRepeat(initial={'arena':cont['arena']})
    cont['form']= form
    return render(request, 'slots/slot-create.html', cont)

@login_required(login_url='login')
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
            is_error=False
            if st>=et:
                messages.error(request, 'End time should be after start time')
                is_error=True
            if sd>ed:
                messages.error(request, 'End date should be after start date')
                is_error=True
            if request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_player_capacity'))>arena.max_player_capacity:
                    messages.error(request, "Player capacity can't be more than max player capacity of the arena")
                    is_error=True
            if request.POST.get('current_spectator_capacity')!='':
                if int(request.POST.get('current_spectator_capacity'))>arena.max_spectator_capacity:
                    messages.error(request, "Spectator capacity can't be more than max spectator capacity of the arena")
                    is_error=True
            if not is_error:
                dt=sd
                while dt<=ed:
                    slot=Slot(
                        name=request.POST.get('name'),
                        arena=arena,
                        start_time=datetime.combine(dt,st),
                        end_time=datetime.combine(dt,et),
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

@login_required(login_url='login')
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
            is_error=False
            if st>=et:
                messages.error(request, 'End time should be after start time')
                is_error=True
            if sd>ed:
                messages.error(request, 'End date should be after start date')
                is_error=True
            if request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_player_capacity'))>arena.max_player_capacity:
                    messages.error(request, "Player capacity can't be more than max player capacity of the arena")
                    is_error=True
            if request.POST.get('current_spectator_capacity')!='':
                if int(request.POST.get('current_spectator_capacity'))>arena.max_spectator_capacity:
                    messages.error(request, "Spectator capacity can't be more than max spectator capacity of the arena")
                    is_error=True
            if not is_error:
                for day in days_list:
                    initial_offset=(int(day)-sd.weekday())%7
                    dt=sd+timedelta(days=initial_offset)
                    while dt<=ed:
                        slot=Slot(
                            name=request.POST.get('name'),
                            arena=arena,
                            start_time=datetime.combine(dt,st),
                            end_time=datetime.combine(dt,et),
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


@login_required(login_url='login')
def slotEdit(request, sport_id, arena_id, slot_id):
    cont=context(request, sport_id, arena_id, slot_id)
    if request.method == 'POST':
        form = SlotCreationFormNoRepeat(request.POST, instance=cont['slot'])
        if form.is_valid():
            is_error=False
            if form.cleaned_data.get('start_time')>=form.cleaned_data.get('end_time'):
                messages.error(request, 'End time should be after start time')
                is_error=True
            if request.POST.get('current_player_capacity')!='':
                if int(request.POST.get('current_player_capacity'))>cont['slot'].arena.max_player_capacity:
                    messages.error(request, "Player capacity can't be more than max player capacity of the arena")
                    is_error=True
            if request.POST.get('current_spectator_capacity')!='':
                if int(request.POST.get('current_spectator_capacity'))>cont['slot'].arena.max_spectator_capacity:
                    messages.error(request, "Spectator capacity can't be more than max spectator capacity of the arena")
                    is_error=True
            if not is_error:
                form.save()
                messages.success(request, f'Slot {cont["slot"]} has been updated!')
                return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    else:
        form = SlotCreationFormNoRepeat(instance=cont['slot'])
    cont['form']=form
    return render(request, 'slots/slot-edit.html', cont)

@login_required(login_url='login')
def slotDelete(request, sport_id, arena_id, slot_id):
    cont=context(request, sport_id, arena_id, slot_id)
    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            n=cont['slot'].name
            cont['slot'].delete()
            messages.success(request, f'Slot "{n}" has been deleted successfully')
            return redirect(reverse('arena-home', args=[sport_id, arena_id]))
    else:
        form = ConfirmationForm()
    cont['form']=form
    return render(request, 'slots/slot-delete.html', cont)

@login_required(login_url='login')
def slotBook(request, sport_id, arena_id, slot_id):
    s=Slot.objects.get(id=slot_id)
    b=Booking(member=request.user, slot=s)
    b.save()
    if Booking.AUTO_APPROVE:
        messages.success(request, f'Booking for slot "{s}" has been approved!')
    else:
        messages.success(request, f'Booking for slot "{s}" has been requested')
    return redirect(reverse('arena-home', args=[sport_id, arena_id]))

@login_required(login_url='login')
def slotCancel(request, sport_id, arena_id, slot_id, member_id):
    cont=context(request, sport_id, arena_id, slot_id)
    b=Booking.objects.get(member_id=member_id, slot_id=slot_id)
    if cont['isstaff'] or cont['isadmin'] or request.user==b.member:
        b.cancel()
        messages.success(request, f"{b.member.get_full_name()}'s booking for slot '{b.slot}' has been cancelled")
    else:
        messages.error(request, "You are not allowed to perform this action. Contact admin if you think this is a mistake.")
    return redirect(reverse('arena-home', args=[sport_id, arena_id]))

@login_required(login_url='login')
def slotCancelAll(request, sport_id, arena_id, slot_id):
    cont=context(request, sport_id, arena_id, slot_id)
    if cont['isstaff'] or cont['isadmin']:
        for b in cont['slot'].booking_set.all():
            b.cancel()
        messages.success(request, f'All bookings for slot \"{cont["slot"]}\" have been cancelled')
    else:
        messages.error(request, "You are not allowed to perform this action. Contact admin if you think this is a mistake.")
    return redirect(reverse('arena-home', args=[sport_id, arena_id]))


@login_required(login_url='login')
def sportRatingCreate(request, sport_id):
    cont=context(request, sport_id)
    if cont['sport'].sportrating_set.filter(member=request.user):
        messages.warning(request, 'You have already submitted a review for this sport. Submitting the below form deletes your previous review.')
        return redirect(reverse('sport-rating-edit', args=[sport_id]))
    if request.method == 'POST':
        form = SportRatingCreationForm(request.POST)
        valid_pars=True
        for par in RATING_PARAMETERS_LIST:
            if request.POST.get(par)=='0':
                messages.error(request, f"Rating for {par.replace('_',' ').capitalize()} can't be empty")
                valid_pars=False
                break
        if form.is_valid() and valid_pars:
            rev=SportRating(
                sport=cont['sport'],
                member=request.user,
                comments=request.POST.get('comments')
            )
            rev.save()
            for par in RATING_PARAMETERS_LIST:
                rat=RatingParameter(
                    rating_group=rev,
                    parameter=par,
                    rating=request.POST.get(par)
                )
                rat.save()
            messages.success(request, 'Your review has been recorded!')
            return redirect(reverse('sport-home', args=[sport_id]))
    else:
        form = SportRatingCreationForm()
    cont['form']= form
    cont['rating_nums']=['-',1,2,3,4,5,6,7,8,9,10]
    return render(request, 'slots/sport-rating-create.html', cont)

@login_required(login_url='login')
def sportRatingEdit(request, sport_id):
    cont=context(request, sport_id)
    if request.method == 'POST':
        form = SportRatingCreationForm(request.POST)
        valid_pars=True
        for par in RATING_PARAMETERS_LIST:
            if request.POST.get(par)=='0':
                messages.error(request, f"Rating for {par.replace('_',' ').capitalize()} can't be empty")
                valid_pars=False
                break
        if form.is_valid() and valid_pars:
            old_rev=SportRating.objects.get(sport=cont['sport'],member=request.user)
            old_rev.delete()
            rev=SportRating(
                sport=cont['sport'],
                member=request.user,
                comments=request.POST.get('comments')
            )
            rev.save()
            for par in RATING_PARAMETERS_LIST:
                rat=RatingParameter(
                    rating_group=rev,
                    parameter=par,
                    rating=request.POST.get(par)
                )
                rat.save()
            messages.success(request, 'Your review has been recorded!')
            return redirect(reverse('sport-home', args=[sport_id]))
    else:
        form = SportRatingCreationForm()
    cont['form']= form
    cont['rating_nums']=['-',1,2,3,4,5,6,7,8,9,10]
    return render(request, 'slots/sport-rating-edit.html', cont)

@login_required(login_url='login')
def sportRatingDelete(request, sport_id):
    cont=context(request, sport_id)
    rev=cont['sport'].sportrating_set.filter(member=request.user)
    if rev:
        rev.first().delete()
        messages.success(request, 'Your review has been deleted')
    return redirect(reverse('sport-home', args=[sport_id]))
