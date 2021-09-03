from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ROLES = (
  ('O', 'Owner'),
  ('R', 'Renter')
)

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLES, help_text='Required. select either Owner/Renter')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role',)