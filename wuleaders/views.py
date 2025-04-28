"""
views.py
File to store all views that correspond to each url; views contain logic to get/post information and render each html page

Last edited:
4.25.27 by Jenna - added additional documentation comments
"""

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
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.views import LoginView
import json

logger = logging.getLogger(__name__)


def club_page_view(request, slug):
  """
  View that corresponds with getting information to make a club's page;
  If user is not logged in, sent to login page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session
    slug: unique slug that represents which club being accessed

  Outputs:
    the club's page if user is logged in, otherwise the login page; home page if some error has occurred
  """
  # if user is just getting the page information
  if request.method == "GET":
    # checking if the user is logged in
    if request.user.is_authenticated:
      member = Member.objects.get(user = request.user)
      try:
        # getting the club that the page is of
        club = Club.objects.get(slug = quote_plus(slug))
        # determining if the user is an editor of the club
        if member in club.editors:
          editor = True
        else:
          editor = False
        # determining if the user is a follower of the club
        if member in club.followers:
          follower = True
        else:
          follower = False

        # creating dictionary of each member of the club and their corresponding role
        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, 'club-page.html', {'request': request, 'club': club, 'member': member, 'editor': editor, 'follower': follower, 'member_roles_dict': member_roles_dict})
      # if slug does not correspond with a Club object
      except Club.DoesNotExist:
        raise Http404
    # user is not logged in
    return redirect(reverse('login'))

  # user is posting information; in this case toggling the follow button
  elif request.method == "POST":
    # checking if the user is logged in
    if request.user.is_authenticated:
      member = Member.objects.get(user = request.user)
      try:
        # getting the club the page is a part of
        club = Club.objects.get(slug = quote_plus(slug))
        
        # if the user is already a follower, remove them as a follower
        if member in club.followers:
          role_obj = Role.objects.get(role = "Follower", club = club)
          role_obj.delete()
          member.save()
          follower = False
        # if the user is not a follower, add them as a follower
        else:
          role_obj = Role.objects.create(
            role = "Follower",
            club = club
          )
          member.roles.add(role_obj)
          member.clubs.add(club)
          member.save()
          follower = True

        # creating dictionary of each member of the club and their corresponding role
        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, 'club-page.html', {'request': request, 'club': club, 'member': member, 'editor': False, 'follower': follower, 'member_roles_dict': member_roles_dict})
      # if slug does not correspond with a Club object
      except Club.DoesNotExist:
        raise Http404
    # user is not logged in
    return redirect(reverse('login'))
  
  # some error has occurred and the request is not GET or POST
  return redirect(reverse('home'))


def edit_club_page_view(request, slug):
  """
  View that corresponds with getting information to make the edit club page; 
  If user is not logged in, sent to login/home page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session
    slug: unique slug that represents which club being accessed

  Outputs:
    the club's page if user is logged in and/or edit successful, otherwise the home/login page
  """
  # getting user info
  user = request.user
  member = Member.objects.get(user = user)
  try:
    # getting the club the page corresponds to
    club = Club.objects.get(slug = quote_plus(slug))
  # if the slug doesn't correspond to a Club object
  except Club.DoesNotExist:
    raise Http404
  # checking the user is logged in and able to edit
  if user.is_authenticated and member in club.editors:

    # edited information is being submitted
    if request.method == "POST":
      form = EditClubForm(request.POST, request.FILES)
      # making sure form has all correct info
      if form.is_valid():
        picture = form.cleaned_data["picture"]
        club.photo = picture
        club.save()

        # creating dictionary of each member of the club and their corresponding role
        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, "club-page.html", {'request': request, 'club': club, 'member': member, 'editor': True, 'member_roles_dict': member_roles_dict})
      # form has errors in it; try again
      else:
        return render(request, "edit-club-page.html", {'request': request, 'form': form})

    # GET request, creating blank form for user to fill in
    else:
      form = EditClubForm()
      return render(request, "edit-club-page.html", {'request': request, 'form': form})
  
  # user should not be on this page, send them to home
  return redirect(reverse("home"))


def edit_club_members_view(request, slug):
  """
  View that corresponds with getting information to make the edit club members page; 
  If user is not logged in, sent to home page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session
    slug: unique slug that represents which club being accessed

  Outputs:
    the club's page if user is logged in and/or edit successful, otherwise the home/login page
  """
  # getting user and checking if they're logged in
  user = request.user
  if user.is_authenticated:

    # user is just accessing page
    if request.method == "GET":
      member = Member.objects.get(user = user)
      try:
        # getting specific club
        club = Club.objects.get(slug = quote_plus(slug))
      # if slug doesn't correspond to Club object
      except ClubDoesNotExist:
        raise Http404
      
      # creating dictionary of each member and follower of the club and their role
      member_roles_dict = {}
      for person in club.memberlist:
        role = list(filter(lambda _role: _role.club == club, person.roleslist))
        member_roles_dict[person] = role[0]
      for follower in club.followers:
        role = list(filter(lambda _role: _role.club == club, follower.roleslist))
        member_roles_dict[follower] = role[0]

      return render(request, "edit-members.html", {'request': request, 'user': user, 'member': member, 'club': club, 'member_roles_dict': member_roles_dict})
    
    # user submitted editing changes
    elif request.method == "POST":
      member = Member.objects.get(user = user)
      try:
        # getting specific club
        club = Club.objects.get(slug = quote_plus(slug))
      # if slug doesn't correspond to Club object
      except ClubDoesNotExist:
        raise Http404
      
      # creating dictionary of each member of the club and their role
      member_roles_dict = {}
      for person in club.memberlist:
        role = list(filter(lambda _role: _role.club == club, person.roleslist))
        member_roles_dict[person] = role[0]
      for follower in club.followers:
        role = list(filter(lambda _role: _role.club == club, follower.roleslist))
        member_roles_dict[follower] = role[0]
      
      # getting edited information from the POST for each member of the club
      for person, role_obj in member_roles_dict.items():
        membership = request.POST.get(f"{person.name} membership", False)
        role = request.POST.get(f"{person.name} role", False)
        editing = request.POST.get(f"{person.name} editing", False)

        # remove person as member
        if not membership:
          person.clubs.remove(club)
          person.roles.remove(role_obj)
          person.save()
        else:
          # update role
          role_obj.role = role
          # add or remove person as editor of club
          if editing:
            role_obj.can_edit = True
          else:
            role_obj.can_edit = False

        role_obj.save()
        person.save()
        
      return redirect(reverse('club-page', args=(club.slug,)))

  # user should not be on this page, send them home
  return redirect(reverse("home"))


def make_post_view(request, slug):
  """
  View that corresponds with getting information to make the make post page; 
  If user is not logged in, sent to home page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session
    slug: unique slug that represents which club being accessed

  Outputs:
    the club's page if user is logged in and/or make post successful, otherwise the home/login page
  """
  # getting info about user
  user = request.user
  member = Member.objects.get(user = user)
  try:
    # get specific club
    club = Club.objects.get(slug = quote_plus(slug))
  # if slug doesn't correspond to a Club object
  except Club.DoesNotExist:
    raise Http404
  # checking if user is logged in and has editing privileges
  if user.is_authenticated and member in club.editors:

    # user submitted post to be made
    if request.method == "POST":
      form = PostForm(request.POST, request.FILES, club_obj = club)
      # all post info is there and correct
      if form.is_valid():
        picture = form.cleaned_data['picture']
        caption = form.cleaned_data['caption']

        # create Post object from form
        post = Post.objects.create(
          image = picture,
          caption = caption,
          posted_at = timezone.now() 
        )
        authors = form.cleaned_data['collaborators']
        post.authors.add(club)
        # add any collaborators as authors
        if authors != None:
          for author in authors:
            post.authors.add(Club.objects.get(club_name = author))
        post.save()

        # make dictionary of club members and their roles
        member_roles_dict = {}
        for person in club.memberlist:
          role = list(filter(lambda _role: _role.club == club, person.roleslist))
          member_roles_dict[person] = role[0]

        return render(request, "club-page.html", {'request': request, 'club': club, 'member': member, 'editor': True, 'member_roles_dict': member_roles_dict})
      # post info wasn't all there or correct; try again
      else:
        return render(request, "make-post.html", {'request': request, 'form': form})
    
    # GET request, make blank form for the user to fill in with post info
    else:
      form = PostForm(club_obj = club)
    return render(request, "make-post.html", {'request': request, 'form': form})
  
  # user should not be here; send them to home
  return redirect(reverse("home"))


def delete_post_view(request, slug, post_id):
  """
  View that corresponds with getting information to delete a club post; 
  Redirected to club-page url view

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session
    slug: unique slug that represents which club being accessed
    post_id: unique id that represents which post is being deleted

  Outputs:
    redirect to club-page url view
  """
  # get info about post, user, and club
  post = Post.objects.get(id=post_id)
  user = request.user
  member = Member.objects.get(user = user)
  club = Club.objects.get(slug = slug)

  # checking if the user is logged in and has editing privileges
  if user.is_authenticated and member in club.editors:

    # clicked delete post button
    if request.method == "POST":
        post.delete()
        return redirect(reverse('club-page', args=(slug,))) 

  # redirecting to club-page url view anyways because it will send anything else to correct place
  return redirect(reverse('club-page', args=(slug,)))


def login_view(request):
  """
  View that corresponds with getting information to make the login page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Outputs:
    if user successfully logs in, sent to home page, otherwise still at login page
  """
  # user submitted login credentials
  if request.method == "POST":
    form = LoginForm(request.POST)
    # all fields are filled in to login
    if form.is_valid():
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      # check if user exists with given information; None if no user exists otherwise the User object
      user = authenticate(request, username = email, password = password)
      # user provided correct credentials; log them in
      if user is not None:
        login(request, user)
        member = Member.objects.get(user = user)

        # get posts that will show up on user's feed sorted by most recent
        posts_dict = {}
        posts_dates = []
        for club in member.clublist:
          for post in club.postlist:
            posts_dict[post.posted_at] = post
            posts_dates.append(post.posted_at)
        posts_dates = sorted(posts_dates, reverse = True)

        return render(request, 'home.html', {'request': request, 'user': user, 'member': member, 'posts_dict': posts_dict, 'posts_dates': posts_dates})
      # user provided wrong credentials; try again
      else:
        return render(request, 'auth/login.html', {'request': request, 'form': form, 'error': "User Not Found"})
    # user didn't provide all required information; try again
    else:
      return render(request, 'auth/login.html', {'request': request, 'form': form, 'error': "Not Valid"})
  
  # GET request, make blank login form for user to fill in
  else:
    form = LoginForm()
  return render(request, 'auth/login.html', {'request': request, 'form': form})


def home_view(request):
  """
  View that corresponds with getting information to make the home page; 
  If user is not logged in, sent to home page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Outputs:
    the home page, personalized if the user is logged in
  """
  user = request.user
  # checking if the user is logged in
  if user.is_authenticated:
    member = Member.objects.get(user = user)

    # make list of posts from the clubs the user follows/is a member of, most recent first
    posts_dict = {}
    posts_dates = []
    for club in member.clublist:
      for post in club.postlist:
        if not post in posts_dict.values():
          posts_dict[post.posted_at] = post
          posts_dates.append(post.posted_at)
    posts_dates = sorted(posts_dates, reverse = True)

    return render(request, 'home.html', {'request': request, 'user': user, 'member': member, 'posts_dict': posts_dict, 'posts_dates': posts_dates})
  
  # user is not logged in
  else:
    return render(request, "home.html", {'request': request})

def member_page_view(request, user_id):
  """
  View that corresponds with getting information to make the member page; 
  If user is not logged in, sent to home page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session
    user_id: unique id of the user to view their own profile page

  Outputs:
    the club's page if user is logged in and/or edit successful, otherwise the home/login page
  """
  user = request.user
  # checking if the user is logged in
  if user.is_authenticated:
    member = Member.objects.get(user_id = user_id)
    # if clicked on their own name, sent to their profile page; otherwise taken to other member page
    if user == member.user:
      return redirect(reverse('profile'))

    return render(request, 'member-page.html', {'request': request, 'member': member})
  # user not logged in; sent home
  else:
    return render(request, "home.html", {'request': request})

def profile_view(request):
  """
  View that corresponds with getting information to make the profile page; 
  If user is not logged in, sent to home page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Outputs:
    the user's profile if logged in, home otherwise
  """
  user = request.user
  # checking if the user is logged in
  if user.is_authenticated:
    member = Member.objects.get(user = user)

    return render(request, 'profile.html', {'request': request, 'user': user, 'member': member})
  
  # user is not logged in; send them home
  else:
    return render(request, "home.html", {'request': request})

def edit_profile_view(request):
  """
  View that corresponds with getting information to make the edit profile page; 
  If user is not logged in, sent to login/home page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Outputs:
    the user's profile page if user is logged in and/or edit successful, otherwise the home/login page
  """
  user = request.user
  # checking if the user is logged in
  if user.is_authenticated:

    # user submitted profile information
    if request.method == "POST":
      form = EditProfileForm(request.POST, request.FILES)
      # all fields are taken and correct
      if form.is_valid():
        picture = form.cleaned_data["picture"]
        pronouns = form.cleaned_data["pronouns"]

        # add profile pic and/or pronouns if any were uploaded
        member = Member.objects.get(user = user)
        member.photo = picture
        member.pronouns = pronouns
        member.save()

        return render(request, "profile.html", {'request': request, 'user': user, 'member': member})
      
      # form has errors in it; try again
      else:
        return render(request, "edit-profile.html", {'request': request, 'form': form})
    
    # GET request, make empty form for user to fill in
    else:
      form = EditProfileForm()
      return render(request, "edit-profile.html", {'request': request, 'form': form})
  
  # user not logged in; send them home
  return redirect(reverse("home"))


def signup_view(request):
  """
  View that corresponds with getting information to make the signup page; 

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Outputs:
    the signup page for users to create an account and be taken to home page once account is created
  """
  # user has submitted information to sign up for an account
  if request.method == "POST":
    form = SignupForm(request.POST)
    # user provided all correct information
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      
      # make sure only people with Willamette students are making accounts
      if "@willamette.edu" in email:
        users = User.objects.all()
        for user in users:
          if user.email == email:
            # premade account for club presidents and advisors being accessed
            if user.last_login == None:
              if user.first_name == first_name:
                user.set_password = password
                user.save()
                member = Member.objects.get(user = user)
                return render(request, 'auth/signup.html', {'request': request, 'user': user, 'member': member})
              # name entered doesn't match what is on Willamette website associated with that email; try again
              else:
                return render(request, 'auth/signup.html', {'error': "Make sure name is correct", 'form': form})
            # an account with provided email already exists and is being used; try again
            return render(request, 'auth/signup.html', {'error': "Email already used for an account", 'form': form})
        
        # passed all checks, free to make new account
        user = User.objects.create_user(username = email, email = email, password = password, first_name = first_name, last_name = last_name)
        member = Member.objects.create(user = user)
        return render(request, 'auth/signup.html', {'request': request, 'user': user, 'member': member})
      
      # not a Willamette email
      else:
        return render(request, 'auth/signup.html', {'error': "Email must be valid Willamette email", 'form': form})
    # not all/correct information provided
    else:
      return render(request, 'auth/signup.html', {'error': "Please make sure all information is entered and valid", 'form': form})
  
  # GET request, create empty form for user to fill in
  else:
    form = SignupForm()
  return render(request, 'auth/signup.html', {'form': form})


def directory_view(request):
  """
  View that corresponds with getting information to make the directory page; 

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Outputs:
    the directory, doesn't matter if user is logged in or not as people can view it without an account as they can on Willamette website
  """
  # user is accessing page, populate with list of clubs
  if request.method == "GET":
    clublist = Club.objects.all()
    return render(request, "directory.html", {'request': request, 'clublist': clublist})
  # any other request method
  else:
    return render(request, "directory.html", {'request': request})

def logout_view(request):
  """
  View that corresponds with getting information to make the logout page

  Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Outputs:
    the home page once the user is logged out
  """
  # making sure user is logged in to be logged out
  if request.user.is_authenticated:
    logout(request)
  return redirect(reverse('home'))


class NotFound(base.View):
  """
  Class view that corresponds with raising the not found page, http404

  Function Inputs:
    request: HTTP request through the url; to GET or POST and contains info about user and session

  Function Outputs:
    Http404
  """
  def get(self, request):
    raise Http404
    
not_found = NotFound.as_view()