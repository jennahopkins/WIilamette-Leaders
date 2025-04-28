"""
urls.py
File to store all url paths and patterns as the user navigates the app

Last edited:
4.27.25 by Jenna - added additional documentation comments
"""

from django.urls import path
from .views import *
import os, environ
from. import views

# setting the environment and base directory that the below urls add on to
env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# list of possible urls for the website and which views they correspond with
urlpatterns = [
  path('', home_view, name = "home"), # home page
  path('signup', signup_view, name ="signup"), # signup page
  path("login", views.login_view, name = "login"), # login page
  path("profile", profile_view, name = "profile"), # user profile page
  path("edit-profile", edit_profile_view, name = "edit-profile"), # user edit profile page
  path("directory", directory_view, name = "directory"), # directory page
  path("member/<str:user_id>", member_page_view, name = "member-page"), # member page
  path('club/<str:slug>', club_page_view, name = "club-page"), # club page
  path('club/<str:slug>/edit', edit_club_page_view, name = "edit-club-page"), # edit club page
  path("club/<str:slug>/make-post", make_post_view, name = "make-post"), # make post page
  path("club/<str:slug>/edit-members", edit_club_members_view, name = "edit-members"), # edit club members page
  path('club/<str:slug>/<int:post_id>/delete/', delete_post_view, name='delete-post'), # delete post function
  path('logout', logout_view, name="logout"), # logout function
  path('not-found', not_found, name="not-found") # not found page
]