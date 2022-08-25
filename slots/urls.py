from django.urls import path
from slots import views as slot_views

urlpatterns = [
    path('', slot_views.sportHome, name='sport-home'),
    path('edit/', slot_views.sportEdit, name='sport-edit'),
    path('delete/', slot_views.sportDelete, name='sport-delete'),
    path('arena/new/', slot_views.arenaCreate, name='arena-create'),
    path('arena/<int:arena_id>/', slot_views.arenaHome, name='arena-home'),
    path('arena/<int:arena_id>/edit/', slot_views.arenaEdit, name='arena-edit'),
    path('arena/<int:arena_id>/delete/', slot_views.arenaDelete, name='arena-delete'),
    path('arena/<int:arena_id>/slot/new/n/', slot_views.slotCreateNoRepeat, name='slot-create-no-repeat'),
    path('arena/<int:arena_id>/slot/new/d/', slot_views.slotCreateDaily, name='slot-create-daily'),
    path('arena/<int:arena_id>/slot/new/w/', slot_views.slotCreateWeekly, name='slot-create-weekly'),
    path('arena/<int:arena_id>/slot/<int:slot_id>/edit/', slot_views.slotEdit, name='slot-edit'),
    path('arena/<int:arena_id>/slot/<int:slot_id>/delete/', slot_views.slotDelete, name='slot-delete'),
]
