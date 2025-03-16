from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_seed import Seed
from ...models import *
import json
import os 
import shutil
dir_path = os.path.dirname(os.path.realpath(__file__))

class Command(BaseCommand):
  help = 'Seeds the database with club data'
  seeder = Seed.seeder()
  json_file = open(dir_path + '/data/' + 'clubs.json')
  json_data = json.load(json_file)

  
  def seed_articles(self):
    for club in self.json_data:
      self.seeder.add_entity(Club, 1, {
        'club_name': club,
        'description': club['description'],
        'president_name': club['president']['name'],
        'president_email': club['president']['email'],
        'advisor_name': club['advisor']['name']
        'advisor_email': club['advisor']['email']
      })
      #User.objects.create_user(name = club['president']['name'], email = club['president']['email'])
      #User.objects.create_user(name = club['advisor']['name'], email = club['advisor']['email'])
  #User.objects.create_user(name = "Jenna Hopkins", email = "jhopkins2@willamette.edu", password = "jhopkins2")
    


  def handle(self, *args, **options):
    print('Seeding database starting . . .')
    try:
      print('Seeding database . . .')
      self.seed_about()
      self.seed_articles()
      self.seed_comments()
      path_list = [
        ['about', 'jennys-blog.png'],
        ['about', 'jenny_image.png'],
        ['article-water-splash', 'water-splash.png'],
        ['article-ready-for-king-winther', 'ready-for-king-winther.png'],
        ['article-homemade-pizza', 'homemade-pizza.png'],
      ]
      for img_folder, img_file in path_list:
        media_path = os.path.join('/home/app/w3s-dynamic-storage/media/uploads', img_folder, img_file)
        try:
          os.makedirs(os.path.dirname(media_path))
        except:
          pass
        static_path = os.path.join('/home/app/blog/static/img', img_file)
        shutil.copy(static_path, media_path)
      self.seeder.execute()
      print('Seeding database completed!')
    except Exception as e:
      print('Seeding database failed . . .')
      print(e)
      raise Exception