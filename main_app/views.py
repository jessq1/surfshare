from django.shortcuts import render, redirect
from .models import Board, Photo, Profile, Reservation
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import SignUpForm, UserForm, ProfileForm, AdjustFundForm, ReservationForm
from .time import Calendar_week, Reservation_check
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from datetime import date, timedelta
import uuid
import boto3

S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'surfshare'

# Create your views here.

class Home(LoginView):
  template_name = 'home.html'

def about(request):
  return render(request, 'about.html')

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      user = form.save()
      user.refresh_from_db() 
      user.profile.role = form.cleaned_data.get('role')
      user.save()
      raw_password = form.cleaned_data.get('password1')
      user = authenticate(username=user.username, password=raw_password)
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Invalid sign up - try again'
  form = SignUpForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'signup.html', {'form': form})

@login_required
def boards_index(request):
    boards = Board.objects.all()
    return render(request, 'boards/index.html', { 'boards': boards }) 

@login_required
def boards_detail(request, board_id):
  board = Board.objects.get(id=board_id)
  calendar_week = Calendar_week()
  reservation_check = Reservation_check()
  board_reservation = Reservation.objects.filter(board=board)
  user = request.user
  reservation_form = ReservationForm()
  adjust_fund_Form = AdjustFundForm()
  return render(request, 'boards/detail.html', { 
    'board': board, 'calendar_week': calendar_week, 'board_reservation':board_reservation,
    'reservation_check': reservation_check, 'reservation_form':reservation_form, 'user':user, 'adjust_fund_Form': adjust_fund_Form, })

class BoardCreate(LoginRequiredMixin, CreateView):
  model = Board
  fields = ['name', 'length', 'description', 'type', 'color', 'price']
  success_url = '/boards/'

  def form_valid(self, form):
    form.instance.user = self.request.user 
    return super().form_valid(form)

class BoardUpdate(LoginRequiredMixin, UpdateView):
  model = Board
  fields = ['name', 'length', 'description', 'type', 'color', 'price']

class BoardDelete(LoginRequiredMixin, DeleteView):
  model = Board
  success_url = '/boards/'

@login_required
def add_photo(request, board_id):
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex + photo_file.name[photo_file.name.rfind('.'):]
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      photo = Photo(url=url, board_id=board_id)
      board_photo = Photo.objects.filter(board_id=board_id)
      if board_photo.first():
        board_photo.first().delete()
      photo.save()
    except Exception as err:
      print('An error occurred uploading file to S3: %s' % err)
  return redirect('boards_detail', board_id=board_id)

@login_required
def profiles_detail(request):
  user_form = UserForm(instance=request.user)
  profile_form = ProfileForm(instance=request.user.profile)
  calendar_week = Calendar_week()
  user_current_reservations = Reservation.objects.filter(user_id=request.user.id, date__range=[date.today(),date.today()+timedelta(days=7)])
  user_past_reservations = Reservation.objects.filter(user_id=request.user.id,date__lt=date.today() )

  return render(request, 'profiles/detail.html', { 
    "user":request.user, "user_form":user_form, "profile_form":profile_form,'calendar_week':calendar_week,  'user_current_reservations':user_current_reservations, 'user_past_reservations':user_past_reservations, })

class ProfileUpdate(LoginRequiredMixin, UpdateView):
  model = Profile
  fields = ['role','fund']

@login_required
def add_reservation(request, board_id):
  form = ReservationForm(request.POST)
  current_user = request.user
  current_board = Board.objects.get(id=board_id)
  if form.is_valid():
    new_reservation = form.save(commit=False)
    new_reservation.board_id = board_id
    new_reservation.user_id = current_user.id
    current_user.profile.fund = current_user.profile.fund - current_board.price
    current_board.user.profile.fund += current_board.price*.8
    new_reservation.save()
    current_user.profile.save()
    current_board.user.profile.save()

  return redirect('boards_detail', board_id=board_id)

class ReservationDetail(LoginRequiredMixin, DetailView):
  model = Reservation
  date = date.today()

class ReservationDelete(LoginRequiredMixin, DeleteView):
  model = Reservation
  success_url = '/profile/'