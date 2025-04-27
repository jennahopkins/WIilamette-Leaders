import logging
import re
from urllib.parse import quote_plus
from copy import deepcopy
from django.db import IntegrityError
from django.views.generic import FormView, base
from django.urls import reverse
from django.shortcuts import HttpResponse, redirect, render
from django.http import Http404, HttpResponseServerError
from .models import *
from .forms import *
from .forms import PostForm, EditProfileForm
from .utilities import *
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import LoginForm
from django.contrib.auth.views import LoginView
import json

logger = logging.getLogger(__name__)


def club_page_view(request, slug):
  if request.method == "GET":
    if request.user.is_authenticated:
      member = Member.objects.get(user = request.user)
      try:
        club = Club.objects.get(slug = quote_plus(slug))
        if member in club.editors:
          editor = True
        else:
          editor = False

        if member in club.followers:
          follower = True
        else:
          follower = False

        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, 'club-page.html', {'request': request, 'club': club, 'member': member, 'editor': editor, 'follower': follower, 'member_roles_dict': member_roles_dict})
      except Club.DoesNotExist:
        raise Http404
    return redirect(reverse('login'))
  elif request.method == "POST":
    if request.user.is_authenticated:
      member = Member.objects.get(user = request.user)
      try:
        club = Club.objects.get(slug = quote_plus(slug))
        if member in club.followers:
          role_obj = Role.objects.get(role = "Follower", club = club)
          role_obj.delete()
          member.save()
          follower = False
        else:
          role_obj = Role.objects.create(
            role = "Follower",
            club = club
          )
          member.roles.add(role_obj)
          member.clubs.add(club)
          member.save()
          follower = True

        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, 'club-page.html', {'request': request, 'club': club, 'member': member, 'editor': False, 'follower': follower, 'member_roles_dict': member_roles_dict})
      except Club.DoesNotExist:
        raise Http404
    return redirect(reverse('login'))
      
  return redirect(reverse('login'))


def edit_club_page_view(request, slug):
  user = request.user
  member = Member.objects.get(user = user)
  try:
    club = Club.objects.get(slug = quote_plus(slug))
  except Club.DoesNotExist:
    raise Http404
  if user.is_authenticated and member in club.editors:
    if request.method == "POST":
      form = EditClubForm(request.POST, request.FILES)
      if form.is_valid():
        picture = form.cleaned_data["picture"]

        club.photo = picture
        club.save()

        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, "club-page.html", {'request': request, 'club': club, 'member': member, 'editor': True, 'member_roles_dict': member_roles_dict})
      else:
        return render(request, "edit-club-page.html", {'request': request, 'form': form})
    else:
      form = EditClubForm()
      return render(request, "edit-club-page.html", {'request': request, 'form': form})
  
  return redirect(reverse("login"))


def edit_club_members_view(request, slug):
  user = request.user
  if user.is_authenticated:
    if request.method == "GET":
      member = Member.objects.get(user = user)
      try:
        club = Club.objects.get(slug = quote_plus(slug))
      except ClubDoesNotExist:
        raise Http404
      
      member_roles_dict = {}
      for person in club.memberlist:
        role = list(filter(lambda _role: _role.club == club, person.roleslist))
        member_roles_dict[person] = role[0]

      return render(request, "edit-members.html", {'request': request, 'user': user, 'member': member, 'club': club, 'member_roles_dict': member_roles_dict})
    elif request.method == "POST":
      member = Member.objects.get(user = user)
      try:
        club = Club.objects.get(slug = quote_plus(slug))
      except ClubDoesNotExist:
        raise Http404
      
      member_roles_dict = {}
      for person in club.memberlist:
        role = list(filter(lambda _role: _role.club == club, person.roleslist))
        member_roles_dict[person] = role[0]
      
      for person, role_obj in member_roles_dict.items():
        membership = request.POST[f"{person.name} membership"]
        role = request.POST[f"{person.name} role"]
        editing = request.POST[f"{person.name} editing"]

        if not membership:
          person.clubs_set.remove(club)
        role_obj.role = role
        if editing:
          role_obj.can_edit = True
        else:
          role_obj.can_edit = False

        role_obj.save()
        person.save()
        
      return redirect(reverse('club-page', args=(club.slug,)))

  return redirect(reverse("login"))


def make_post_view(request, slug):
  user = request.user
  member = Member.objects.get(user = user)
  try:
    club = Club.objects.get(slug = quote_plus(slug))
  except Club.DoesNotExist:
    raise Http404
  if user.is_authenticated and member in club.editors:
    if request.method == "POST":
      form = PostForm(request.POST, request.FILES, club_obj = club)
      if form.is_valid():
        picture = form.cleaned_data['picture']
        caption = form.cleaned_data['caption']

        post = Post.objects.create(
          image = picture,
          caption = caption,
          posted_at = timezone.now() 
        )
        authors = form.cleaned_data['collaborators']
        post.authors.add(club)
        if authors != None:
          for author in authors:
            post.authors.add(Club.objects.get(club_name = author))
        post.save()

        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, "club-page.html", {'request': request, 'club': club, 'member': member, 'editor': True, 'member_roles_dict': member_roles_dict})
      else:
        return render(request, "edit-club-page.html", {'request': request, 'form': form})
    else:
      form = PostForm(club_obj = club)
    return render(request, "make-post.html", {'request': request, 'form': form})
  
  return redirect(reverse("login"))

def delete_post_view(request, slug, post_id):
  post = Post.objects.get(id=post_id)
  user = request.user
  member = Member.objects.get(user = user)
  club = Club.objects.get(slug = slug)

  if user.is_authenticated and member in club.editors:
    if request.method == "POST":
        post.delete()
        return redirect(reverse('club-page', args=(slug,))) 

  return redirect(reverse('club-page', args=(slug,)))





def login_view(request):
  if request.method == "POST":
    form = LoginForm(request.POST)
    if form.is_valid():
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      user = authenticate(request, username = email, password = password)
      if user is not None:
        login(request, user)
        member = Member.objects.get(user = user)

        posts_dict = {}
        posts_dates = []
        for club in member.clublist:
          for post in club.postlist:
            posts_dict[post.posted_at] = post
            posts_dates.append(post.posted_at)
        posts_dates = sorted(posts_dates, reverse = True)

        return render(request, 'home.html', {'request': request, 'user': user, 'member': member, 'posts_dict': posts_dict, 'posts_dates': posts_dates})
      else:
        return render(request, 'auth/login.html', {'request': request, 'form': form, 'error': "User Not Found"})
    else:
      return render(request, 'auth/login.html', {'request': request, 'form': form, 'error': "Not Valid"})
  else:
    form = LoginForm()
  return render(request, 'auth/login.html', {'request': request, 'form': form})


def home_view(request):
  user = request.user
  if user.is_authenticated:
    member = Member.objects.get(user = user)

    posts_dict = {}
    posts_dates = []
    for club in member.clublist:
      for post in club.postlist:
        if not post in posts_dict.values():
          posts_dict[post.posted_at] = post
          posts_dates.append(post.posted_at)
    posts_dates = sorted(posts_dates, reverse = True)

    return render(request, 'home.html', {'request': request, 'user': user, 'member': member, 'posts_dict': posts_dict, 'posts_dates': posts_dates})
  else:
    return render(request, "home.html", {'request': request})

def member_page_view(request, user_id):
  user = request.user
  if user.is_authenticated:
    member = Member.objects.get(user_id = user_id)
    if user == member.user:
      return redirect(reverse('profile'))
    return render(request, 'member-page.html', {'request': request, 'member': member})
  else:
    return render(request, "home.html", {'request': request})

def profile_view(request):
  user = request.user
  if user.is_authenticated:
    member = Member.objects.get(user = user)

    return render(request, 'profile.html', {'request': request, 'user': user, 'member': member})
  else:
    return render(request, "home.html", {'request': request})

def edit_profile_view(request):
  user = request.user
  if user.is_authenticated:
    if request.method == "POST":
      form = EditProfileForm(request.POST, request.FILES)
      if form.is_valid():
        picture = form.cleaned_data["picture"]
        pronouns = form.cleaned_data["pronouns"]

        member = Member.objects.get(user = user)
        member.photo = picture
        member.pronouns = pronouns
        member.save()

        return render(request, "profile.html", {'request': request, 'user': user, 'member': member})
      else:
        return render(request, "edit-profile.html", {'request': request, 'form': form})
    else:
      form = EditProfileForm()
      return render(request, "edit-profile.html", {'request': request, 'form': form})
  
  return redirect(reverse("login"))


def signup_view(request):
  if request.method == "POST":
    form = SignupForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      if "@willamette.edu" in email:
        users = User.objects.all()
        for user in users:
          if user.email == email:
            if user.last_login == None:
              if user.first_name == first_name:
                user.set_password = password
                user.save()
                member = Member.objects.get(user = user)
                return render(request, 'auth/signup.html', {'request': request, 'user': user, 'member': member})
              else:
                return render(request, 'auth/signup.html', {'error': "Make sure name is correct", 'form': form})
            return render(request, 'auth/signup.html', {'error': "Email already used for an account", 'form': form})
        user = User.objects.create_user(username = email, email = email, password = password, first_name = first_name, last_name = last_name)
        member = Member.objects.create(user = user)
        
        return render(request, 'auth/signup.html', {'request': request, 'user': user, 'member': member})
      else:
        return render(request, 'auth/signup.html', {'error': "Email must be valid Willamette email", 'form': form})
    else:
      return render(request, 'auth/signup.html', {'error': "Please make sure all information is entered and valid", 'form': form})
  else:
    form = SignupForm()
  return render(request, 'auth/signup.html', {'form': form})


def directory_view(request):
  if request.method == "GET":
    clublist = Club.objects.all()
    return render(request, "directory.html", {'request': request, 'clublist': clublist})
  else:
    return render(request, "directory.html", {'request': request})

def logout_view(request):
  if request.user.is_authenticated:
    logout(request)
  return redirect(reverse('home'))


class NotFound(base.View):

  def get(self, request):
    raise Http404



not_found = NotFound.as_view()