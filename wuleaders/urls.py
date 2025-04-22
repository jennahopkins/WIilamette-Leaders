from django.urls import path
from .views import *
from .decorators.decorators import authentication_required, if_authenthicated_redirect_from_login
import os, environ
from. import views

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

urlpatterns = [
  path('', home_view, name = "home"),
  path('signup', signup_view, name ="signup"),
  path("login", views.login_view, name = "login"),
  path("profile", profile_view, name = "profile"),
  path("edit-profile", edit_profile_view, name = "edit-profile"),
  path("directory", directory_view, name = "directory"),
  path('club/<str:slug>', club_page_view, name = "club-page"),
  path('club/<str:slug>/edit', edit_club_page_view, name = "edit-club-page"),
  path("club/<str:slug>/make-post", make_post_view, name = "make-post"),
  path("club/<str:slug>/edit-members", edit_club_members_view, name = "edit-members"),
  path('club/<str:slug>/<int:post_id>/delete/', delete_post_view, name='delete-post'),

  path('new-article', authentication_required(new_article_view), name="new-article"),
  path('edit-about', authentication_required(edit_about_view), name="edit-about"),
  path('article/<str:slug>', article_view, name="article"),
  path('article/<str:slug>/edit', authentication_required(edit_article_view), name="edit-article"),
  # LoginView is a built-in Django view
  path(env('LOGIN_ROUTE_PATH'), if_authenthicated_redirect_from_login(login_view), name="login"),
  path('logout', logout_view, name="logout"),
  path('not-found', not_found, name="not-found")
]