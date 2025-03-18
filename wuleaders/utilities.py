import re
import requests
from .models import *
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from django.conf import settings
from django.urls import reverse
from os import listdir, remove, makedirs, rename, rmdir
from os.path import isfile, join, exists
from shutil import rmtree

def set_context(type):
  title = {
    'new-article': 'New Article',
    'edit-article': 'Edit Article',
    'edit-about': 'Edit About',
  }
  return {
    'type': type,
    'title': title.get(type) or '',
  }

def convert_to_string_from_htmlstring(html_string):
  tag_remover = re.compile(r'<.*?>')
  title = tag_remover.sub('', html_string)
  return title.replace(' ', '-').replace('&nbsp;', '').strip().lower()

class ArticleHTMLParser(HTMLParser):
  sources = []
  data = ''
  def handle_starttag(self, tag, attrs):
    if tag == 'img':
      for attr in attrs:
        if attr[0] == 'src':
          self.sources.append(attr[1])
  
  def handle_data(self, data):
    if data:
      self.data = self.data + data
    else:
      '\n'


def set_redirect_url(editor_type, slug=None):
  if editor_type == 'new-article' or editor_type == 'edit-about':
    return reverse('home')
  elif editor_type == 'edit-article' and slug:
    return f'/article/{slug}'
  elif editor_type == 'edit-about':
    return '/'

def get_images_from_request(content):
  soup = BeautifulSoup(content, features='html.parser')
  return [img['src'].rpartition('/')[-1] for img in soup.findAll('img')]

def update_images_in_request(content, folder):
  soup = BeautifulSoup(content, features='html.parser')
  for img in soup.findAll('img'):
    if 'data:' in img['src']:
      continue
    elif '://' in img['src']:
      continue
    else:
      filename = img['src'].rpartition('/')[-1]
      img['src'] = f'/media/uploads/{folder}/{filename}'
  return str(soup)

def move_images_to_folder(filenames, folder):
  uploads_path = join('w3s-dynamic-storage', 'media', 'uploads')
  for filename in filenames:
    try:
      old_filepath = join(uploads_path, filename)
      folder_path = join(uploads_path, folder)
      if not exists(folder_path):
        makedirs(folder_path)
      new_filepath = join(folder_path, filename)
      rename(old_filepath, new_filepath)
    except Exception as e:
      print(e)
      pass

def clear_unused_images():
  uploads_path = join('w3s-dynamic-storage', 'media', 'uploads')
  for filename in listdir(uploads_path):
    filepath = join(uploads_path, filename)
    if isfile(filepath):
      try:
        remove(filepath)
      except:
        pass
    else:
      if len(listdir(filepath)) == 0:
        rmdir(filepath)

def clear_unused_images_from_folder(images, folder):
  folder_path = join('w3s-dynamic-storage', 'media', 'uploads', folder)
  if not exists(folder_path):
    makedirs(folder_path)
  for filename in listdir(folder_path):
    is_file = isfile(join(folder_path, filename))
    no_images = len(images) == 0
    if is_file and (no_images or (filename not in images)):
      filepath = join(folder_path, filename)
      try:
        remove(filepath)
      except Exception as e:
        print(e)
        pass
  if len(listdir(folder_path)) == 0:
    rmdir(folder_path)

def new_images_handler(flow_type, pk=None):
  uploads_path = join('w3s-dynamic-storage', 'media', 'uploads')
  if flow_type == 'delete':
    folder_path = join(uploads_path, f'article-{pk}')
    rmtree(folder_path)
    return
  if not exists(uploads_path):
    makedirs(uploads_path)
  if 'article' in flow_type:
    model_object = Article.objects.get(pk=pk)
    folder = f'article-{model_object.slug}'
  elif 'about' in flow_type:
    model_object = About.objects.get(pk=pk)
    folder = 'about'
  if flow_type != 'cancel':
    model_object.content = update_images_in_request(model_object.content, folder)
    model_object.save()
    images = get_images_from_request(model_object.content)
    if 'edit' in flow_type:
      clear_unused_images_from_folder(images, folder)
    move_images_to_folder(images, folder)
  clear_unused_images()

def set_form_fields(form, **fields):
  form.base_fields['title'].initial = fields['title']
  form.base_fields['content'].initial = fields['content']
  return form

def recaptchaCheck(token):
  params = {
    'response': token,
    'secret': settings.RECAPTCHA_SECRET_KEY
  }
  reCAPCTHA_response = requests.post('https://www.google.com/recaptcha/api/siteverify', params=params).json()
  if reCAPCTHA_response['success'] == False:
    return False
  else:
    return True