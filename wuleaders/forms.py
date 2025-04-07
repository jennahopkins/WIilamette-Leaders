from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from ckeditor.fields import RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingFormField

from .utilities import *
from .models import Post

class PostForm(forms.ModelForm):
  class Meta:
    model = Post
    fields = "__all__"

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
"""class LoginForm(AuthenticationForm):
  email = forms.CharField(
    label='Email:',
    widget=forms.TextInput()
  )
  password = forms.CharField(
    label='Password:', 
    widget=forms.PasswordInput()
  )

  def __init__(self, *args, **kwargs):
    super(LoginForm, self).__init__(*args, **kwargs)

  class Meta:
    model = User
    fields = ('username', 'password',)

  def clean(self, *args, **kwargs):
    username = self.cleaned_data.get('username')
    password = self.cleaned_data.get('password')
    user = authenticate(self, username=username, password=password)
    if user is not None:
      if not user:
        print('No user found')
        raise forms.ValidationError('No user found')
      if not user.is_active:
        print('User is unable to login')
        raise forms.ValidationError('User is unable to login')
      login(self.request, user)
    elif user is None:
      print('Email or password are incorrect')
      raise forms.ValidationError('Email or password are incorrect')
    return super(LoginForm, self).clean(*args, **kwargs)"""

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



  """def __init__(self, *args, **kwargs):
    super(SignupForm, self).__init__(*args, **kwargs)

  class Meta:
    model = User
    fields = ('username', 'password',)

  def clean(self, *args, **kwargs):
    username = self.cleaned_data.get('username')
    password = self.cleaned_data.get('password')
    user = authenticate(self, username=username, password=password)
    if user is not None:
      if not user:
        print('No user found')
        raise forms.ValidationError('No user found')
      if not user.is_active:
        print('User is unable to login')
        raise forms.ValidationError('User is unable to login')
      login(self.request, user)
    elif user is None:
      print('Email or password are incorrect')
      raise forms.ValidationError('Email or password are incorrect')
    return super(SignupForm, self).clean(*args, **kwargs)"""