from django.urls import path
from .views import *
from .decorators.decorators import authentication_required, if_authenthicated_redirect_from_login
import os, environ

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

urlpatterns = [
  path('', if_authenthicated_redirect_from_login(login_view), name='login-home'),
  path('signup', signup_view, name ="signup"),
  path('new-article', authentication_required(new_article_view), name="new-article"),
  path('edit-about', authentication_required(edit_about_view), name="edit-about"),
  path('article/<str:slug>', article_view, name="article"),
  path('article/<str:slug>/edit', authentication_required(edit_article_view), name="edit-article"),
  # LoginView is a built-in Django view
  path(env('LOGIN_ROUTE_PATH'), if_authenthicated_redirect_from_login(login_view), name="login"),
  path('logout', logout_view, name="logout"),
  path('not-found', not_found, name="not-found")
]