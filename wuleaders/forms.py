import logging
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .models import Post, Club

logger = logging.getLogger(__name__)


class LoginForm(forms.Form):
  """
  Form that contains login information

  Fields:
    email: the email the user wishes to login with
    password: the password the user wishes to login with
  """
  email = forms.CharField(
    label='Email:',
    widget=forms.TextInput()
  )
  password = forms.CharField(
    label='Password:', 
    widget=forms.PasswordInput()
  )

class SignupForm(forms.Form):
  """
  Form that contains signup information

  Fields:
    first_name: the first name of the user wishing to sign up
    last_name: the last name of the user wishing to sign up
    email: the email of the user wishing to sign up
    password: the password the user chooses as they sign up
  """
  first_name = forms.CharField(
    label = "First Name",
    widget = forms.TextInput()
  )
  last_name = forms.CharField(
    label = "Last Name",
    widget = forms.TextInput()
  )
  email = forms.CharField(
    label='Email:',
    widget=forms.TextInput()
  )
  password = forms.CharField(
    label='Password:', 
    widget=forms.PasswordInput()
  )

class EditProfileForm(forms.Form):
  """
  Form that contains information about a user's profile

  Fields:
    picture: profile picture the user wishes to use
    pronouns: pronouns the user wishes to use
  """
  # choices of pronouns the user can display
  CHOICES = [
  ('she/her', 'she/her'),
  ('they/them', 'they/them'),
  ('he/him', 'he/him'),
  ('any/all', 'any/all'),
  ('other/ask me', 'other/ask me'),
  ]
  picture = forms.ImageField(
    label = "Profile Picture:",
    widget = forms.ClearableFileInput(),
    required = False
  )
  pronouns = forms.ChoiceField(
    label = "Pronouns: ",
    choices = CHOICES,
    widget = forms.Select(),
    required = False
  )

class EditClubForm(forms.Form):
  """
  Form that contains information about a club

  Fields:
    picture: profile picture a club wishes to use
  """
  picture = forms.ImageField(
    label = "Club Photo:",
    widget = forms.ClearableFileInput(),
    required = False
  )

class PostForm(forms.Form):
  """
  Form that contains information about a post a club makes

  Fields:
    picture: picture that will be used in the post
    caption: the caption that goes with the post
    collaborators: other clubs that are collaborating on this post
  """
  picture = forms.ImageField(
    label = "Post Image:",
    widget = forms.ClearableFileInput(),
    required = False
  )
  caption = forms.CharField(
    label = "Caption:",
    widget = forms.TextInput(),
    required = False
  )
  collaborators = forms.MultipleChoiceField(
    label = "Collaborators",
    choices = [],
    widget = forms.CheckboxSelectMultiple(),
    required = False
  )

  def __init__(self, *args, club_obj = None, **kwargs):
    """
    Initializing function that gets all available collaborators to display to the club

    Inputs:
      club_obj: the Club object that is the current club making the post; will be taken out of available collaborators

    Outputs:
      None
    """
    super().__init__(*args, **kwargs)
    self.club_obj= club_obj
    if club_obj:
      clubs = Club.objects.all()
      CHOICES = []
      for club in clubs:
        if club != club_obj:
          CHOICES.append((club.club_name, club.club_name))
      self.fields['collaborators'].choices = CHOICES



