from django import forms
from .models import Sport, Arena, Slot, SportRating, RatingParameter, RATING_PARAMETERS_LIST
# from .models import Sport, Arena, Slot, ArenaRating, SportRating, RatingParameter, RATING_PARAMETERS_LIST
from django.contrib.admin import widgets as admin_widgets


class ConfirmationForm(forms.Form):
    agree = forms.BooleanField(label='I Agree')


class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name']

class ArenaForm(forms.ModelForm):
    class Meta:
        model = Arena
        fields = '__all__'

class SlotCreationFormNoRepeat(forms.ModelForm):
    start_time = forms.SplitDateTimeField(widget=admin_widgets.AdminSplitDateTime(attrs={'style':'max-width: 15em'}), help_text="Enter time in 24 hour format with colons. Like 6:00 am becomes 6:00, and 5:00 pm becomes 17:00")
    end_time = forms.SplitDateTimeField(widget=admin_widgets.AdminSplitDateTime(attrs={'style':'max-width: 15em'}), help_text="Enter time in 24 hour format with colons. Like 6:00 am becomes 6:00, and 5:00 pm becomes 17:00")
    class Meta:
        model = Slot
        fields = '__all__'

class SlotCreationFormDaily(forms.ModelForm):
    starting_time = forms.TimeField(widget=admin_widgets.AdminTimeWidget(attrs={'style':'max-width: 15em'}), help_text="Enter time in 24 hour format with colons. Like 6:00 am becomes 6:00, and 5:00 pm becomes 17:00")
    ending_time = forms.TimeField(widget=admin_widgets.AdminTimeWidget(attrs={'style':'max-width: 15em'}), help_text="Enter time in 24 hour format with colons. Like 6:00 am becomes 6:00, and 5:00 pm becomes 17:00")
    repeat_daily_starting_from_date = forms.DateField(widget=admin_widgets.AdminDateWidget(attrs={'style':'max-width: 15em'}))
    repeat_daily_until_date = forms.DateField(widget=admin_widgets.AdminDateWidget(attrs={'style':'max-width: 15em'}))
    class Meta:
        model = Slot
        fields = ['name', 'arena', 'starting_time', 'ending_time', 'repeat_daily_starting_from_date', 'repeat_daily_until_date', 'current_player_capacity', 'current_spectator_capacity']

class SlotCreationFormWeekly(forms.ModelForm):
    starting_time = forms.TimeField(widget=admin_widgets.AdminTimeWidget(attrs={'style':'max-width: 15em'}), help_text="Enter time in 24 hour format with colons. Like 6:00 am becomes 6:00, and 5:00 pm becomes 17:00")
    ending_time = forms.TimeField(widget=admin_widgets.AdminTimeWidget(attrs={'style':'max-width: 15em'}), help_text="Enter time in 24 hour format with colons. Like 6:00 am becomes 6:00, and 5:00 pm becomes 17:00")
    repeating_days = forms.MultipleChoiceField(
        choices=[(0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')],
        widget = forms.CheckboxSelectMultiple(),
        help_text='Select one or more days'
    )
    repeat_weekly_starting_from_date = forms.DateField(widget=admin_widgets.AdminDateWidget(attrs={'style':'max-width: 15em'}))
    repeat_weekly_until_date = forms.DateField(widget=admin_widgets.AdminDateWidget(attrs={'style':'max-width: 15em'}))
    class Meta:
        model = Slot
        fields = ['name', 'arena', 'starting_time', 'ending_time', 'repeating_days', 'repeat_weekly_starting_from_date', 'repeat_weekly_until_date', 'current_player_capacity', 'current_spectator_capacity']

class SportRatingCreationForm(forms.ModelForm):
    for par in RATING_PARAMETERS_LIST:
        exec(par+"=forms.IntegerField(widget=forms.widgets.NumberInput(attrs={'type':'range', 'min':0, 'max':10, 'step':1, 'value':'0', 'class': 'w-100'}))")
    class Meta:
        model = SportRating
        fields = ['comments']
