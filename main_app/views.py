from django.shortcuts import render, redirect
# from .models import Plant, Pot, Photo
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import SignUpForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import uuid
# import boto3

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