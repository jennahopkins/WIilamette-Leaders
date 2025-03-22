import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_seed import Seed
from ...models import *
from ...models import Member, Club, Role
import json
import os 
import shutil
dir_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)

class Command(BaseCommand):
  help = 'Seeds the database with club data'
  json_file = open(dir_path + '/data/' + 'clubs.json')
  json_data = json.load(json_file)
  logger = logging.getLogger(__name__)
  Club.objects.all().delete()
  User.objects.all().delete()
  Role.objects.all().delete()
  Member.objects.all().delete()
  
  def populate_clubs(self):
    for club in self.json_data:
      try:
        club_obj = Club.objects.create(
            club_name = club,
            description = self.json_data[club]['description'],
            president_name = self.json_data[club]['president']['name'],
            president_email = self.json_data[club]['president']['email'],
            advisor_name = self.json_data[club]['advisor']['name'],
            advisor_email = self.json_data[club]['advisor']['email'],
            slug = club.replace(" ", "-")
        )

        try:
          user = User.objects.get(username = self.json_data[club]['president']['email'])
          role_obj = Role.objects.create(
            role = "President",
            club = club_obj
          )
          member = Member.objects.get(user = user)
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
        except User.DoesNotExist:
          name = self.json_data[club]['president']['name'].split(" ", 1)
          user = User.objects.create_user(
            username = self.json_data[club]['president']['email'], 
            email = self.json_data[club]['president']['email'], 
            first_name = name[0],
            last_name = name[1]
            )
          member = Member.objects.create(user = user)
          role_obj = Role.objects.create(
            role = "President",
            club = club_obj
          )
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
        
        try:
          user = User.objects.get(username = self.json_data[club]['advisor']['email'])
          role_obj = Role.objects.create(
            role = "Advisor",
            club = club_obj
          )
          member = Member.objects.get(user = user)
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
        except User.DoesNotExist:
          name = self.json_data[club]['advisor']['name'].split(" ", 1)
          user = User.objects.create_user(
            username = self.json_data[club]['advisor']['email'], 
            email = self.json_data[club]['advisor']['email'], 
            first_name = name[0],
            last_name = name[1]
            )
          member = Member.objects.create(user = user)
          role_obj = Role.objects.create(
            role = "Advisor",
            club = club_obj
          )
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
      except:
        pass
    try:
      User.objects.get(username="jhopkins2@willamette.edu")
    except User.DoesNotExist:
      User.objects.create_user(username = "jhopkins2@willamette.edu", password = "jhopkins2")
  
  
  def handle(self, *args, **options):
    print('Populating database starting . . .')
    try:
      print('Populating database . . .')
      self.populate_clubs()
      print('Populating database completed!')
    except Exception as e:
      print('Populating database failed . . .')
      print(e)
      raise Exception