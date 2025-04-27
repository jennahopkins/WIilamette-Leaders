"""import logging
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
  seeder = Seed.seeder()
  json_file = open(dir_path + '/data/' + 'clubs.json')
  json_data = json.load(json_file)
  logger = logging.getLogger(__name__)
  Club.objects.all().delete()
  User.objects.all().delete()
  Role.objects.all().delete()
  Member.objects.all().delete()
  
  def seed_clubs(self):
    for club in self.json_data:
      try:
        self.seeder.add_entity(Club, 1, {
          'club_name': club,
          'description': self.json_data[club]['description'],
          'president_name': self.json_data[club]['president']['name'],
          'president_email': self.json_data[club]['president']['email'],
          'advisor_name': self.json_data[club]['advisor']['name'],
          'advisor_email': self.json_data[club]['advisor']['email'],
          'slug': club.replace(" ", "-")
        })
        try:
          User.objects.get(username = self.json_data[club]['president']['email'])
        except User.DoesNotExist:
          name = self.json_data[club]['president']['name'].split(" ", 1)
          User.objects.create_user(
            username = self.json_data[club]['president']['email'], 
            email = self.json_data[club]['president']['email'], 
            first_name = name[0],
            last_name = name[1]
            )

          """self.seeder.add_entity(Member, 1, {
          'user': user,
          'clubs': club_obj,
          'roles': role
          })"""
      
        try:
          User.objects.get(username = self.json_data[club]['advisor']['email'])
        except User.DoesNotExist:
          name = self.json_data[club]['advisor']['name'].split(" ", 1)
          user = User.objects.create_user(
            username = self.json_data[club]['advisor']['email'], 
            email = self.json_data[club]['advisor']['email'], 
            first_name = name[0],
            last_name = name[1]
            )
          #role = Role.objects.create(club = club, role = "Advisor")
          #member = Member.objects.create(user = user)
          #member.clubs.add(*club)
          #member.roles.add(*role)
          #member.save()
      except:
        pass
    try:
      User.objects.get(username="jhopkins2@willamette.edu")
    except User.DoesNotExist:
      User.objects.create_user(username = "jhopkins2@willamette.edu", password = "jhopkins2")
  
  def seed_roles_members(self):
    member_list = []
    for club in Club.objects.all():
      self.seeder.add_entity(Role, 1, {
        'club': club,
        'role': "President"
      })
      president_first_name = club.president_name.split(" ", 1)[0]
      president_last_name = club.president_name.split(" ", 1)[1]
      president = User.objects.get(first_name = president_first_name, last_name = president_last_name)
      if president not in member_list:
        self.seeder.add_entity(Member, 1, {
        'user': president
        })
        member_list.append(president)
      advisor_first_name = club.advisor_name.split(" ", 1)[0]
      advisor_last_name = club.advisor_name.split(" ", 1)[1]
      advisor = User.objects.get(first_name = advisor_first_name, last_name = advisor_last_name)
      if advisor not in member_list:
        self.seeder.add_entity(Member, 1, {
        'user': advisor
        })
        member_list.append(advisor)

  def handle(self, *args, **options):
    print('Seeding database starting . . .')
    try:
      print('Seeding database . . .')
      self.seed_clubs()
      self.seeder.execute()
      print("Seeding clubs completed")
      self.seed_roles_members()
      self.seeder.execute()
      for club in Club.objects.all():
        president_first_name = club.president_name.split(' ', 1)[0]
        president_last_name = club.president_name.split(" ", 1)[1]
        president = User.objects.get(first_name = president_first_name, last_name = president_last_name)
        member = Member.objects.get(user = president)
        role = Role.objects.get(club = club)
        logger.warning(member.user.first_name)
        logger.warning(club.club_name)
        logger.warning(role.club.club_name)
        member.clubs.add(club)
        member.roles.add(role)
        member.save()
      print("Seeding roles and members completed")
      print('Seeding database completed!')
    except Exception as e:
      print('Seeding database failed . . .')
      print(e)
      raise Exception"""