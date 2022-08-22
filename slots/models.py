from django.db import models

class Sport(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Arena(models.Model):
    name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    location = models.URLField(help_text="Google maps link for the location", blank=True, null=True)
    max_player_capacity = models.PositiveSmallIntegerField()
    max_spectator_capacity = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class Slot(models.Model):
    name = models.CharField(max_length=100, default='(Untitled)')
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    current_player_capacity = models.PositiveSmallIntegerField(blank=True)
    current_spectator_capacity = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def duration(self):
        return self.end_time-self.start_time

    def save(self, *args,**kwargs):
        self.current_player_capacity=self.arena.max_player_capacity
        self.current_spectator_capacity=self.arena.max_spectator_capacity
        return super().save(*args,**kwargs)