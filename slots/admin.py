from django.contrib import admin
from .models import Sport,Arena,Slot,Booking,ArenaRating,SportRating,RatingParameter

admin.site.register(Sport)
admin.site.register(Arena)
admin.site.register(Slot)
admin.site.register(Booking)
admin.site.register(ArenaRating)
admin.site.register(SportRating)
admin.site.register(RatingParameter)
