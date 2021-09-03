from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLES = (
  ('O', 'Owner'),
  ('R', 'Renter')
)

TYPES = (
  ('H', 'Hard Top'),
  ('S', 'Soft Top')
)

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=1,choices=ROLES,default=ROLES[0][0])
    fund = models.FloatField(default='0')

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Board(models.Model):
  name = models.CharField(max_length=100)
  length = models.CharField(max_length=100)
  description = models.TextField(max_length=250)
  type = models.CharField(max_length=1,choices=TYPES,default=TYPES[0][0])
  color = models.CharField(max_length=20)
  price = models.IntegerField()
#   reservation = models.ManyToManyField(Reservation)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f"{self.get_type_display()}"
  
  def get_absolute_url(self):
    return reverse('boards_detail', kwargs={'board_id': self.id})


class Photo(models.Model):
  url = models.CharField(max_length=250)
  board = models.OneToOneField(Board, on_delete=models.CASCADE)

  def __str__(self):
    return f"Photo for board_id: {self.board_id} @{self.url}"