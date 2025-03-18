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

  
  def seed_clubs(self):
    for club in self.json_data:
      self.seeder.add_entity(Club, 1, {
        'club_name': club,
        'description': self.json_data[club]['description'],
        'president_name': self.json_data[club]['president']['name'],
        'president_email': self.json_data[club]['president']['email']
        #'advisor_name': self.json_data[club]['advisor']['name'],
        #'advisor_email': self.json_data[club]['advisor']['email']
      })
      try:
        User.objects.get(username = self.json_data[club]['president']['email'])
        #User.objects.get(username = self.json_data[club]['advisor']['email'])
      except User.DoesNotExist:
        User.objects.create_user(username = self.json_data[club]['president']['email'])
        #User.objects.create_user(username = self.json_data[club]['advisor']['email'])
    
    try:
      User.objects.get(username="jhopkins2@willamette.edu")
    except User.DoesNotExist:
      User.objects.create_user(username = "jhopkins2@willamette.edu", password = "jhopkins2")


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