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
  json_file = open(dir_path + '/data/' + 'seed-data-blank.json')
  json_data = json.load(json_file)

  def seed_about(self):
    self.seeder.add_entity(About, 1, self.json_data['about'])
  
  def seed_articles(self):
    for index in range(1,4):
      self.seeder.add_entity(Article, 1, {
        'id': index,
        'slug': 'article'+'-'+str(index),
        'title': self.json_data['article']['title'],
        'content': self.json_data['article']['content'],
        'views': self.json_data['article']['views']
      })
  
  def seed_comments(self):
    for index in range(1,4):
      self.seeder.add_entity(Comment, 3, {
        'article_id': index,
        'content': self.json_data['comment']['content'],
      })

  def handle(self, *args, **options):
    print('Seeding database starting . . .')
    try:
      print('Seeding database . . .')
      self.seed_about()
      self.seed_articles()
      self.seed_comments()
      path_list = [
        ['about', 'template-profile-picture.png'],
        ['article-article', 'template-thumbnail.png'],
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