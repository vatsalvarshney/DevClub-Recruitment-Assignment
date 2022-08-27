from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from datetime import datetime, timedelta
from django.conf import settings

class Role(models.Model):
    admin = 1
    staff = 2
    member = 3
    role_choices = (
        (admin, 'Admin'),
        (staff, 'Staff'),
        (member, 'Member')
    )
    
    id=models.PositiveSmallIntegerField(choices=role_choices,primary_key=True)

    def __str__(self):
        return self.get_id_display()

def pfpUpload(instance, filename):
    new_path=os.path.join('users/profile-pics', instance.username+'.'+filename.split('.')[-1])
    full_path=os.path.join(settings.MEDIA_ROOT,new_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    return new_path

class User(AbstractUser):
    role = models.ManyToManyField(Role)
    profile_picture = models.ImageField(upload_to=pfpUpload, default='users/default-pfp.jpg')

    def roles(self):
        return "; ".join([r.get_id_display() for r in self.role.all()])
    
    def total_played_minutes(self):
        ans=timedelta()
        for bk in self.booking_set.filter(slot__end_time__lt=datetime.now(), is_active=True):
            ans+=bk.slot.duration()
        return ans.seconds//60
