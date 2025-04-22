import logging
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from ckeditor.fields import RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingFormField

from .utilities import *
from .models import Post, Club

logger = logging.getLogger(__name__)

class CkEditorArticleForm(forms.Form):
  title = RichTextFormField(
    config_name="title-article-editor"
  )
  content = RichTextUploadingFormField(
    config_name="content-editor"
  )

class CkEditorAboutForm(forms.Form):
  title = RichTextFormField(
    config_name="title-about-editor"
  )
  content = RichTextUploadingFormField(
    config_name="content-editor"
  )

class LoginForm(forms.Form):
  email = forms.CharField(
    label='Email:',
    widget=forms.TextInput()
  )
  password = forms.CharField(
    label='Password:', 
    widget=forms.PasswordInput()
  )

class SignupForm(forms.Form):
  first_name = forms.CharField(
    label = "First Name: ",
    widget = forms.TextInput()
  )
  last_name = forms.CharField(
    label = "Last Name: ",
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
  picture = forms.ImageField(
    label = "Club Photo:",
    widget = forms.ClearableFileInput(),
    required = False
  )

class PostForm(forms.Form):

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
    super().__init__(*args, **kwargs)
    self.club_obj= club_obj
    if club_obj:
      clubs = Club.objects.all()
      CHOICES = []
      for club in clubs:
        if club != club_obj:
          CHOICES.append((club.club_name, club.club_name))
      self.fields['collaborators'].choices = CHOICES



