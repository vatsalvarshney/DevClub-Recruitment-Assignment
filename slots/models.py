from django.db import models
from users.models import User

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

    def save(self, *args,**kwargs):
        self.current_player_capacity=self.arena.max_player_capacity
        self.current_spectator_capacity=self.arena.max_spectator_capacity
        return super().save(*args,**kwargs)

# class Booking(models.Model):
#     member = models.ForeignKey(User, on_delete=models.CASCADE)
#     slot = models.ForeignKey(Slot, on_delete=models.CASCADE)