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





class ArticleView(base.View):

  def get(self, request, slug):
    is_auth = request.user.is_authenticated
    context = {}
    context['is_authenticated'] = is_auth
    context['site_key'] = settings.RECAPTCHA_SITE_KEY
    referer = ''
    if 'HTTP_REFERER' in request.META:
      referer = request.META.get('HTTP_REFERER')
    if 'request_error' in request.session:
      # Can be:
      # - Failed to save comment.
      # - Failed to delete comment.
      # - 500 - Server error.
      if request.session['request_error'] == 'Failed to save comment.':
        context['request_error_content'] = request.session['request_error_content']
      context['request_error'] = request.session['request_error']
      del request.session['request_error']
    try:
      article = Article.objects.get(slug=quote_plus(slug))
      context['article'] = article
      if not "article" in referer:
        try:
          article.views = article.views + 1
          article.save()
        except Exception as e:
          print(e)
      try:
        comments = Comment.objects.filter(article_id=article.id)
        for comment in comments:
          comment.content = comment.content.strip()
        context['comments'] = reversed(comments)
        article.total_comments = len(comments)       
      except Comment.DoesNotExist:
        context['request_error'] = "Comments not found."
      except Exception as e:
        print(e)
        context['request_error'] = 'Failed to retrieve comments.'
      try:
        about = About.objects.get(id=1)
        context['about'] = about
      except About.DoesNotExist:
        context['request_error'] = 'Title not found.'
      except Exception as e:
        context['request_error'] = 'Failed to retrieve blog title.'
      finally:
        return render(request, 'article.html', context)
    except Article.DoesNotExist:
      raise Http404
    except Exception as e:
      print(e)
      context['request_error'] = 'Server error'
      return redirect(reverse('home'))

  def post(self, request, slug):
    is_auth = request.user.is_authenticated
    context = {}
    context['is_authenticated'] = is_auth
    try:
      article = Article.objects.get(slug=slug)

      if 'add_comment_form' in request.POST:
        recaptchaVerified = recaptchaCheck(request.POST['g-recaptcha-response'])
        if recaptchaVerified:
          try:
            Comment(article_id=article.id, content=request.POST['content']).save()
            return redirect(reverse('article', args = [slug]))
          except Exception as e:
            print(e)
            request.session['request_error'] = 'Failed to save comment.'
            request.session['request_error_content'] = request.POST['content']
            request.session['request_error_type'] = 'save'
            return redirect(reverse('article', args = [slug]))
        else:
          request.session['request_error'] = 'Recaptcha failed.'
          return redirect(reverse('article', args = [slug]))

      elif 'delete_comments_form' in request.POST:
        try:
          objects_to_delete = [int(x) for x in request.POST['form_data'].split(',')]
          Comment.objects.filter(id__in=objects_to_delete).delete()
          return redirect(reverse('article', args = [slug]))
        except Exception as e:
          print(e)
          request.session['request_error'] = 'Failed to delete comment.'
          request.session['request_error_type'] = 'delete'
          return redirect(reverse('article', args = [slug]))
    except Article.DoesNotExist:
      request.session['request_error'] = 'Article not found.'
      return redirect(reverse('article', args = [slug]))
    except Exception as e:
      print(e)
      request.session['request_error'] = '500 - Server error'
      return redirect(reverse('article', args = [slug]))


class CKEditor(FormView):
  extra_context = {}

  def get(self, request, slug=None):
    if not request.user.is_authenticated:
      raise Http404
    context = deepcopy(self.extra_context)

    if context['type'] == 'new-article':
      form = CkEditorArticleForm
      form = set_form_fields(form, title=None, content=None)
      if 'request_error' in request.session:
        form = set_form_fields(form, title=request.session['request_error_content']['title'], content=request.session['request_error_content']['content'])
        context['request_error'] = request.session['request_error']
      context['form'] = form
      return render(request, 'text-editor.html', context)

    elif context['type'] == 'edit-about':
      form = CkEditorAboutForm
      form = set_form_fields(form, title=None, content=None)
      if 'request_error' in request.session:
        form = set_form_fields(form, title=request.session['request_error_content']['title'], content=request.session['request_error_content']['content'])
        context['request_error'] = request.session['request_error']
      context['form'] = form
      try:
        about = About.objects.get(id=1)
        form = set_form_fields(form, title=about.title, content=about.content)
        return render(request, 'text-editor.html', context)
      except About.DoesNotExist:
        About(title='', content='').save()
        return render(request, 'text-editor.html', context)
      except Exception as e:
        print(e)
        return HttpResponseServerError()

    elif context['type'] == 'edit-article':
      form = CkEditorArticleForm
      form = set_form_fields(form, title=None, content=None)
      if 'request_error' in request.session:
        form = set_form_fields(form, title=request.session['request_error_content']['title'], content=request.session['request_error_content']['content'])
        context['request_error'] = request.session['request_error']

      context['form'] = form
      try:
        article = Article.objects.get(slug=slug)
        form = set_form_fields(form, title=article.title, content=article.content)
        context['href'] = f'/article/{slug}' if context['type'] == 'edit-article' else '/'
        return render(request, 'text-editor.html', context)
      except Article.DoesNotExist:
        return HttpResponseServerError()
      except Exception as e:
        print(e)
        return HttpResponseServerError()
# CKEditor post
  def post(self, request, slug=None):
    if 'request_error' in request.session:
      del request.session['request_error']
    if not request.user.is_authenticated:
      raise Http404
    context = deepcopy(self.extra_context)
    if 'save' in request.POST:
      if context['type'] == 'new-article':
        title = convert_to_string_from_htmlstring(request.POST['title'])
        if title in ['', '.', '..']:
          request.session['request_error'] = 'Title cannot be empty or contain only period(s)'
          request.session['request_error_content'] = {'title': request.POST['title'], 'content': request.POST['content']}
          return redirect(reverse('new-article'))
        i = 0
        while True:
          slug = re.sub(r"[^a-zA-Z0-9-_]", "", title)
          try:
            if i > 0:
              slug = f'{slug}-{i}'
            article = Article(title=request.POST['title'], slug=slug, content=request.POST['content'])
            article.save()
            new_images_handler('new-article', pk=article.pk)
            return redirect(reverse('article', args = [slug]))
          except IntegrityError:
            #infinite loop safety cord
            if i > 10:
              print('Too many tries. This means that i is greater than 10 which could indicate a problem in the code or 10 identical slugs.')
              request.session['request_error'] = 'Server failed.'
              return redirect(reverse('home'))
            print(slug)
            i += 1
            continue
          except Exception as e:
            print(e)
            request.session['request_error'] = 'Failed to save article.'
            request.session['request_error_content'] = {'title': request.POST['title'], 'content': request.POST['content']}
            return redirect(reverse('new-article'))

      elif context['type'] == 'edit-article':
        title = convert_to_string_from_htmlstring(request.POST['title'])
        if title in ['', '.', '..']:
          request.session['request_error'] = 'Title cannot be empty or contain only period(s)'
          request.session['request_error_content'] = {'title': request.POST['title'], 'content': request.POST['content']}
          return redirect(reverse('edit-article', args = [slug]))
        try:
          article = Article.objects.get(slug=slug)
          new_slug = re.sub(r"[^a-zA-Z0-9-_]", "", title)
          article.title=request.POST['title']
          article.content=request.POST['content']
          article.slug = new_slug
          article.save()
          new_images_handler('edit-article', pk=article.pk)
        except Article.DoesNotExist:
          print(e)
          return HttpResponseServerError()
        except Exception as e:
          print(e)
          request.session['request_error'] = 'Failed to save article.'
          request.session['request_error_content'] = {'title': request.POST['title'], 'content': request.POST['content']}
          return redirect(reverse('article', args = [new_slug]))
        return redirect(reverse('article', args = [new_slug]))

      elif context['type'] == 'edit-about':
        try:
          about = About.objects.get(id=1)
          about.title = request.POST['title']
          about.content = request.POST['content']
          about.save()
          new_images_handler('edit-about', pk=about.pk)
          return redirect(reverse('home'))
        except About.DoesNotExist:
          try:
            about = About(title=request.POST['title'], content=request.POST['content'])
            about.save()
            new_images_handler('new-about', pk=about.pk)
            return redirect(reverse('home'))
          except Exception as e:
            print(e)
            request.session['request_error'] = 'Failed to save content.'
            request.session['request_error_content'] = {'title': request.POST['title'], 'content': request.POST['content']}
            return redirect(reverse('edit-about'))
        except Exception as e:
          print(e)
          return HttpResponseServerError()

    elif 'cancel' in request.POST:
      new_images_handler('cancel')
      redirect_url = set_redirect_url(context['type'], slug)
      return redirect(redirect_url)

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