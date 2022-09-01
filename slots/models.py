from django.db import models
from users.models import User
import statistics

class Sport(models.Model):
    name = models.CharField(max_length=50)
    cover_picture = models.ImageField(blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cover_picture = f'slots/sport-covers/sport-cover-{(self.id)%5 + 1}.jpeg'
        return super().save(*args, **kwargs)


class Arena(models.Model):
    name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    location = models.URLField(help_text="Google maps link for the location (Optional)", blank=True, null=True)
    max_player_capacity = models.PositiveSmallIntegerField()
    max_spectator_capacity = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Slot(models.Model):
    name = models.CharField(max_length=100, default='(Untitled)')
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    current_player_capacity = models.PositiveSmallIntegerField(help_text='Default is the max player capacity of the arena', blank=True)
    current_spectator_capacity = models.PositiveSmallIntegerField(help_text='Default is the max spectator capacity of the arena', blank=True, null=True)

    def __str__(self):
        return self.name

    def duration(self):
        return self.end_time-self.start_time
    
    def approved_booking_set(self):
        return self.booking_set.filter(is_approved=True, is_active=True)

    def approved_member_set(self):
        return self.approved_booking_set().values_list('member', flat=True)

    def cancelled_member_set(self):
        return self.booking_set.filter(is_active=False).values_list('member', flat=True)

    def approved_booking_count(self):
        return self.approved_booking_set().count()

    def available_booking_count(self):
        ans = self.current_player_capacity-self.approved_booking_count()
        if ans>=0:
            return ans
        else:
            return "O/B"    # Overbooked

    def save(self, *args,**kwargs):
        if self.current_player_capacity==None:
            self.current_player_capacity=self.arena.max_player_capacity
        if self.current_spectator_capacity==None:
            self.current_spectator_capacity=self.arena.max_spectator_capacity
        return super().save(*args,**kwargs)


class Booking(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)

    AUTO_APPROVE = True    # Automatic approval of bookings
    is_approved = models.BooleanField(default=AUTO_APPROVE)
    is_active = models.BooleanField(default=True)

    def approve(self):
        self.is_approved=True
        return self.save()
    
    def cancel(self):
        self.is_active=False
        return self.save()


RATING_PARAMETERS_LIST=[
    'infrastructure',
    'equipment',
    'safety',
    'cleanliness',
    'staff_behaviour',
    'overall_experience'
]
RATINGS_CHOICES = [(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'),(6,'6'),(7,'7'),(8,'8'),(9,'9'),(10,'10')]

class SportRating(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField(help_text="Be civil and respectful. Don't use offensive language.")
    rating_time = models.DateTimeField(auto_now_add=True)

    def net_rating(self):
        return round(statistics.fmean(self.ratingparameter_set.values_list('rating', flat=True)),2)


class RatingParameter(models.Model):
    rating_group = models.ForeignKey(SportRating, on_delete=models.CASCADE)
    parameter = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(choices=RATINGS_CHOICES)

    def get_parameter_display(self):
        return self.parameter.replace('_',' ').capitalize()
