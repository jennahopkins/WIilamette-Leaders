"""
populate_clubs.py
Provides a command to be used in the terminal to populate the clubs and users based on the clubs.json file with information from Willamette's website

Last edited:
4.27.25 by Jenna - provide additional documentation comments
"""

import logging
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.contrib.auth.models import User
from django_seed import Seed
from ...models import *
from ...models import Member, Club, Role, Post
import json
import os 
import shutil
dir_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)

class Command(BaseCommand):
  """
  Class to provide a command to be used in the terminal to populate the clubs and users based on the clubs.json file

  Variables:
    help: str to help describe class function
    json_file: filename of the file to be read in to get data from (clubs.json)
    json_data: loaded data of the json file
    logger: logger to log messages and warnings to be used in debug
  """ 
  help = 'Seeds the database with club data'
  json_file = open(dir_path + '/data/' + 'clubs.json')
  json_data = json.load(json_file)
  logger = logging.getLogger(__name__)

  # deleting all existing Clubs, Users, Roles, Members, and Posts
  Club.objects.all().delete()
  User.objects.all().delete()
  Role.objects.all().delete()
  Member.objects.all().delete()
  Post.objects.all().delete()
  
  def populate_clubs(self):
    """
    Main helping function to populate the clubs and users based on the file

    Inputs:
      None

    Outputs:
      None
    """
    for club in self.json_data:
      try:
        # create Club object
        club_obj = Club.objects.create(
            club_name = club,
            description = self.json_data[club]['description'],
            president_name = self.json_data[club]['president']['name'],
            president_email = self.json_data[club]['president']['email'],
            advisor_name = self.json_data[club]['advisor']['name'],
            advisor_email = self.json_data[club]['advisor']['email'],
            slug = club.replace(" ", "-")
        )

        # get User and Member objects for the president of the club and create new Role object
        try:
          user = User.objects.get(username = self.json_data[club]['president']['email'])
          role_obj = Role.objects.create(
            role = "President",
            club = club_obj,
            can_edit = True
          )
          member = Member.objects.get(user = user)
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
        # create User, Role, and Member objects for the president of the club if they don't already exist
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
            club = club_obj,
            can_edit = True
          )
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
        
        # get User and Member objects for the advisor of the club and create a new Role object
        try:
          user = User.objects.get(username = self.json_data[club]['advisor']['email'])
          role_obj = Role.objects.create(
            role = "Advisor",
            club = club_obj,
            can_edit = True
          )
          member = Member.objects.get(user = user)
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
        # create User, Role, and Member objects for the advisor of the club if they don't already exist
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
            club = club_obj,
            can_edit = True
          )
          member.clubs.add(club_obj)
          member.roles.add(role_obj)
          member.save()
      # if any errors prevent club from being created, skip it
      except:
        pass

    # get User object for jenna if it exists
    try:
      user = User.objects.get(username="jhopkins2@willamette.edu")
    # create User object for jenna if it doesn't exist
    except User.DoesNotExist:
      user = User.objects.create_user(
        username = "jhopkins2@willamette.edu", 
        password = "jhopkins2",
        email = "jhopkins2@willamette.edu",
        first_name = "Jenna",
        last_name = "Hopkins"
        )
      # make her part of saac and cssa with roles as members
      saac_club = Club.objects.get(club_name = "Student Athlete Advisory Committee")
      cssa_club = Club.objects.get(club_name = "Computer Science Students Association")
      member = Member.objects.create(user = user)
      role_saac = Role.objects.create(
        role = "Member",
        club = saac_club,
        can_edit = True
      )
      role_cssa = Role.objects.create(
        role = "Member",
        club = cssa_club
      )
      member.clubs.add(saac_club)
      member.clubs.add(cssa_club)
      member.roles.add(role_saac)
      member.roles.add(role_cssa)
      member.save()

  
  
  def handle(self, *args, **options):
    """
    Main function ran when the command is used

    Inputs:
      *args and **options: provides places for additional arguments to be passed into the function, by single or dictionary respectively

    Outputs:
      prints to the terminal the status of the function and any exceptions
    """
    print('Populating database starting . . .')
    try:
      # populates database with populate_clubs function
      print('Populating database . . .')
      self.populate_clubs()
      print('Populating database completed!')
    # some error occurred
    except Exception as e:
      print('Populating database failed . . .')
      print(e)
      raise Exception