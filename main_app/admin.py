from django.contrib import admin
from .models import Profile, Board, Photo, Reservation

# Register your models here.
admin.site.register(Profile)
admin.site.register(Board)
admin.site.register(Photo)
admin.site.register(Reservation)
