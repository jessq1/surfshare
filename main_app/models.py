from django.db import models
from django.urls import reverse
from datetime import date, timedelta
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

TIMES = (
  ('5', '5:00AM-6:45AM'),
  ('7', '7:00AM-8:45AM'),
  ('9', '9:00AM-10:45AM'),
  ('11', '11:00AM-12:45PM'),
  ('13', '13:00PM-14:45PM'),
  ('15', '15:00PM-16:45PM'),
  ('17', '17:00PM-18:45PM'),
  ('19', '19:00PM-20:45PM'),
  ('21', '21:00PM-22:45PM'),
)

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=1,choices=ROLES,default=ROLES[0][0])
    fund = models.FloatField(default='0')

    def __str__(self):
      return f"{self.get_role_display()}"

    def get_absolute_url(self):
      return reverse('profiles_detail')

    def get_current_reservation_table(self):
      table=[]
      for time in TIMES:
        tb_row = [time[1]]
        for i in range(0,7):
          if self.user.reservation_set.filter(date=(date.today()+timedelta(days=i)), time=time[0]).exists():
            tb_row.append(self.user.reservation_set.get(date=(date.today()+timedelta(days=i)), time=time[0]))
          else:
            tb_row.append(' ')
        table.append(tb_row)
      return table

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(post_save, sender=User) 
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

class Board(models.Model):
  name = models.CharField(max_length=100)
  length = models.CharField(max_length=100)
  description = models.TextField(max_length=250)
  type = models.CharField(max_length=1,choices=TYPES,default=TYPES[0][0])
  color = models.CharField(max_length=20)
  price = models.IntegerField()
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f"{self.get_type_display()}"
  
  def get_absolute_url(self):
    return reverse('boards_detail', kwargs={'board_id': self.id})

  def get_board_current_reservations(self):
    start_day = date.today()
    end_day = start_day + timedelta(days=7)
    return self.reservation_set.filter(date__range=[start_day, end_day])
  
  def get_all_board_reservations(self):
    return self.reservation_set.all()

  def get_current_reservation_table(self):
    table=[]
    for time in TIMES:
      tb_row = [time[1]]
      for i in range(0,7):
        if self.reservation_set.filter(date=(date.today()+timedelta(days=i)), time=time[0]).exists():
          tb_row.append(self.reservation_set.get(date=(date.today()+timedelta(days=i)), time=time[0]))
        else:
          tb_row.append(' ')
      table.append(tb_row)
    return table

class Reservation(models.Model):
  date = models.DateField()
  time = models.CharField(max_length=2,choices=TIMES,default=TIMES[0][0])

  board= models.ForeignKey(Board, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f"{self.get_time_display()} on {self.date}"
  class Meta:
    ordering = ['date']

  

class Photo(models.Model):
  url = models.CharField(max_length=250)
  board = models.OneToOneField(Board, on_delete=models.CASCADE)

  def __str__(self):
    return f"Photo for board_id: {self.board_id} @{self.url}"