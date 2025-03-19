from django.core.management.base import BaseCommand
from django_seed import Seed
from ...models import *
import json
import os 
import shutil
dir_path = os.path.dirname(os.path.realpath(__file__))

class Command(BaseCommand):
  help = 'Seeds the database with dummy data'
  seeder = Seed.seeder()
  json_file = open(dir_path + '/data/' + 'seed-data.json')
  json_data = json.load(json_file)

  def seed_about(self):
    self.seeder.add_entity(About, 1, self.json_data['about'])
  
  def seed_articles(self):
    for article in self.json_data['articles']:
      self.seeder.add_entity(Article, 1, {
        'id': article['id'],
        'slug': article['slug'],
        'title': article['title'],
        'content': article['content'],
        'views': article['views']
      })
  
  def seed_comments(self):
    for comment in self.json_data['comments']:
      self.seeder.add_entity(Comment, 1, {
        'article_id': comment['article_id'],
        'content': comment['content'],
      })

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
        static_path = os.path.join('/home/app/wuleaders/static/img', img_file)
        shutil.copy(static_path, media_path)
      self.seeder.execute()
      print('Seeding database completed!')
    except Exception as e:
      print('Seeding database failed . . .')
      print(e)
      raise Exception
