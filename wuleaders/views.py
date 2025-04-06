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
from .forms import PostForm
from .utilities import *
from django.contrib.auth import logout as custom_logout
from django.conf import settings
from django.contrib.auth.models import User

from .forms import LoginForm
from django.contrib.auth.views import LoginView
import json

logger = logging.getLogger(__name__)

class HomeView(base.View):

  def get(self, request):
    is_auth = request.user.is_authenticated
    context = {}
    context['is_authenticated'] = is_auth
    if 'request_error' in request.session:
      # Can be:
      # - Article not found.
      # - 500 - Server error.
      # - Server failed.
      context['request_error'] = request.session['request_error']
      del request.session['request_error']
    try:
      context['about'] = About.objects.get(id=1)
    except About.DoesNotExist:
      context['about'] = None
      context['error'] = "About not found."
    except Exception as e:
      print(e)
      context['about'] = None
      context['error'] = '500 - Server error'
    try:
      articles = Article.objects.all().order_by('created_at').reverse()
      context['articles'] = articles
      for article in context['articles']:
        try:
          comments = Comment.objects.filter(article_id=article.id)
        except Exception as e:
          print(e)
          comments=[]
        titleParser = ArticleHTMLParser()
        contentParser = ArticleHTMLParser()
        contentParser.feed(article.content)
        if(contentParser.sources and contentParser.sources[0]):
          article.img_source = contentParser.sources[0]
          article.content = re.sub("(<img.*?>)", "", article.content, 0, re.IGNORECASE | re.DOTALL | re.MULTILINE)
          contentParser.sources.clear()
        contentParser.data = ''
        article.title = re.sub("(<img.*?>)", "", article.title, 0, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        titleParser.feed(article.title)
        contentParser.feed(article.content)
        if(len(titleParser.data) > 45):
          slicer = slice(45)
          article.title = titleParser.data[slicer] + '...'
        else:
          article.title = titleParser.data
        article.content = contentParser.data
        article.total_comments = len(comments)
      return render(request, 'home.html', context)
    except Exception as e:
      print(e)
      context['articles'] = None
      context['error'] = '500 - Server error'
      raise Http404

  def post(self, request):
    try:
      id_list = [int(x) for x in request.POST['id-list'].split(',')]
      for article_id in id_list:
        article = Article.objects.get(id=article_id)
        slug = article.slug
        article.delete()
        new_images_handler('delete', slug)
      return redirect(reverse('home'))

    except Article.DoesNotExist:
      request.session['request_error'] = 'Article not found.'
      return redirect(reverse('home'))
    except Exception as e:
      print(e)
      request.session['request_error'] = '500 - Server error.'
      return redirect(reverse("home"))


class MemberHomeView(base.View):

  def get(self, request):
    is_auth = request.user.is_authenticated
    context = {}
    context['is_authenticated'] = is_auth
    if 'request_error' in request.session:
      # Can be:
      # - Article not found.
      # - 500 - Server error.
      # - Server failed.
      context['request_error'] = request.session['request_error']
      del request.session['request_error']

    member = Member.objects.get(user = request.user.id)
    posts_dict = {}
    posts_dates = []
    for club in member.clublist:
      for post in club.postlist:
        posts_dict[post.posted_at] = post
        posts_dates.append(post.posted_at)
    posts_dates = sorted(posts_dates, reverse = True)

    try:
      context['posts_dict'] = posts_dict
      context['posts_dates'] = posts_dates
    except Exception as e:
      print(e)
      context['error'] = '500 - Server error'

    return render(request, 'member-home.html', context)
    
  def post(self, request):
    try:
      id_list = [int(x) for x in request.POST['id-list'].split(',')]
      for post_id in id_list:
        post = Post.objects.get(id=post_id)
        #slug = article.slug
        #article.delete()
        #new_images_handler('delete', slug)
      return redirect(reverse('member-home'))

    except Post.DoesNotExist:
      request.session['request_error'] = 'Article not found.'
      return redirect(reverse('member-home'))
    except Exception as e:
      print(e)
      request.session['request_error'] = '500 - Server error.'
      return redirect(reverse("member-home"))

def club_page_view(request, slug):
  if request.method == "GET":
    if request.user.is_authenticated:
      member = Member.objects.get(user = request.user)
      try:
        club = Club.objects.get(slug = quote_plus(slug))
        return render(request, 'club-page.html', {'request': request, 'club': club, 'member': member})
      except Club.DoesNotExist:
        raise Http404
    return redirect(reverse('login'))
  return(redirect(reverse('login')))


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
  logger.warning("login view")
  logger.warning(request.session.session_key)
  logger.warning(request.session.items())
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

        logger.warning("login successful")
        logger.warning(request.session.session_key)
        logger.warning(request.session.items())
        request.session.save()
        return render(request, 'home.html', {'request': request, 'user': user, 'member': member, 'posts_dict': posts_dict, 'posts_dates': posts_dates})
      else:
        return render(request, 'auth/login.html', {'request': request, 'form': form, 'errors': form.errors})
  else:
    form = LoginForm()
  return render(request, 'auth/login.html', {'request': request, 'form': form})

def home_view(request):
  logger.warning("home view")
  logger.warning(request.session.session_key)
  logger.warning(request.session.items())
  user = request.user
  if user.is_authenticated:
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
    return render(request, "home.html", {'request': request})

def profile_view(request):
  logger.warning("profile view")
  logger.warning(request.session.items())
  user = request.user
  if user.is_authenticated:
    member = Member.objects.get(user = user)

    return render(request, 'profile.html', {'request': request, 'user': user, 'member': member})
  else:
    return render(request, "home.html", {'request': request})

def signup_view(request):
  if request.method == "POST":
    form = SignupForm(request.POST)
    if form.is_valid():
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      if "@willamette.edu" in email:
        logger.warning("willamette.edu")
        user = User.objects.create_user(username = email, password = password)
        return render(request, 'auth/signup.html', {'user': user})
      else:
        logger.warning("not willamette.edu")
        return render(request, 'auth/signup.html', {'errors': "Email must be valid Willamette email", 'form': form})
    logger.warning("form not valid")
    logger.warning(form.cleaned_data['email'], )
    logger.warning(form.cleaned_data['password'])
  else:
    form = SignupForm()
  return render(request, 'auth/signup.html', {'form': form})


def upload_image_view(request):
  logger.warning("upload image view")
  logger.warning(request)
  logger.warning(request.session.items())
  if request.method == "POST":
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      return render(request, "home.html", {'request': request, 'user': request.user})
  else:
    form = PostForm()
  return render(request, "upload-image.html", {'request': request, 'form': form})

def directory_view(request):
  if request.method == "GET":
    clublist = Club.objects.all()
    return render(request, "directory.html", {'request': request, 'clublist': clublist})
  else:
    return render(request, "directory.html", {'request': request})



class LogoutView(base.View):
   
   def post(self, request):
    if request.user.is_authenticated:
      custom_logout(request)
    return redirect(reverse('home'))

class NotFound(base.View):

  def get(self, request):
    raise Http404


member_home_view = MemberHomeView.as_view()

article_view = ArticleView.as_view()

new_article_view = CKEditor.as_view(extra_context=set_context('new-article'))
edit_about_view = CKEditor.as_view(extra_context=set_context('edit-about'))
edit_article_view = CKEditor.as_view(extra_context=set_context('edit-article'))

logout_view = LogoutView.as_view()
not_found = NotFound.as_view()