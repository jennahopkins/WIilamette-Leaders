import functools
from django.shortcuts import redirect
from django.contrib import messages

def authentication_required(view_func, redirect_url="/not-found"):
  """
      this decorator ensures that a user is not logged in,
      if a user is logged in, the user will get redirected to 
      the url whose view name was passed to the redirect_url parameter
  """
  @functools.wraps(view_func)
  def wrapper(request, *args, **kwargs):
    if request.user.is_authenticated:
      return view_func(request,*args, **kwargs)
    messages.info(request, "You need to be logged in")
    print("You need to be logged in")
    return redirect(redirect_url)
  return wrapper

def if_authenthicated_redirect_from_login(view_func, redirect_url="/"):
  """
      this decorator ensures that if a user is logged in,
      and if a user goes to a login route,
      a user will be redirected to an index page
  """
  @functools.wraps(view_func)
  def wrapper(request):
    if request.user.is_authenticated:
      return redirect(redirect_url)
    return view_func(request)
  return wrapper