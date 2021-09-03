from django.shortcuts import render, redirect
from .models import Board, Photo
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import SignUpForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
#   pots_board_doesnt_have = Pot.objects.exclude(id__in = board.pots.all().values_list('id'))
#   water_form = WaterForm()
  return render(request, 'boards/detail.html', { 
    'board': board, })

class BoardCreate(LoginRequiredMixin, CreateView):
  model = Board
  fields = ['name', 'length', 'description', 'type', 'color', 'price']
  success_url = '/boards/'

  def form_valid(self, form):
    form.instance.user = self.request.user 
    return super().form_valid(form)

class BoardUpdate(LoginRequiredMixin, UpdateView):
  model = Board
  # Let's disallow the renaming of a board by excluding the name field!
  fields = ['origin', 'description', 'age']

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