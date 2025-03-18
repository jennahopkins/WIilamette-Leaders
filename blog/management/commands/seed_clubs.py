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
      president_user = User.objects.create_user(name = club['president']['name'], email = club['president']['email'])
      president_user.save()
      advisor_user = User.objects.create_user(name = club['advisor']['name'], email = club['advisor']['email'])
      advisor_user.save()
  jenna = User.objects.create_user(name = "Jenna Hopkins", email = "jhopkins2@willamette.edu", password = "jhopkins2")
  jenna.save()


  def handle(self, *args, **options):
    print('Seeding database starting . . .')
    try:
      print('Seeding database . . .')
      self.seed_clubs()
      self.seeder.execute()
      print('Seeding database completed!')
    except Exception as e:
      print('Seeding database failed . . .')
      print(e)
      raise Exception