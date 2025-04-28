"""
changeusername.py
Provides a command to be used in the terminal to change the username of an existing user

Last edited:
4.27.25 by Jenna - provide additional documentation comments
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
  """
  Class to provide a command to be used in the terminal to change the username of an existing user

  Variables:
    help: str to help describe class function
  """ 
  help = 'Change username for an existing user.'

  def add_arguments(self, parser):
    """
    Helper function to add arguments to the command

    Inputs:
      parser: the parser that will be used in the command

    Outputs:
      None
    """
    parser.add_argument('username', nargs='?', help="Username to change; by default, it's the current username.")
  
  def _validate_username(self, username):
    """
    Helper function to validate the username entered

    Inputs:
      username: the username that it should be changed to

    Outputs:
      bool: True if username is validated, False if not
    """
    # checking that every character in the username is valid
    valid_chars = 'abcdefghijklmnopqrstuvwxyz0123456789@.+-_'
    for char in username:
      if char.lower() not in valid_chars:
        return False

  def handle(self, *args, **options):
    """
    Main function that runs when the command is called

    Inputs:
      *args and **options: provides places for additional arguments to be passed into the function, by single or dictionary respectively
        **options is used to pass in the username

    Outputs:
      writes to the terminal to inform if the username change was successful or not
    """
    try:
      # get user and new username and validate it
      user = User.objects.get(username=options['username'])
      username = input('New username: ')
      valid = self._validate_username(username)
      # username not validated; inform user of error
      if not valid:
        self.stderr.write(self.style.ERROR('Error: Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'))
      # username validated; change it and inform user of success
      elif len(username) > 0:
        user.username = username
        user.save()
        self.stdout.write(self.style.SUCCESS('Username changed.'))
      # no username provided
      else:
        self.stderr.write(self.style.ERROR('You must provide a username.'))
    
    # inform user of any errors that occur
    except IntegrityError:
      self.stderr.write(self.style.ERROR('This username is already in use.'))
    except User.DoesNotExist:
      self.stderr.write(self.style.ERROR('This user does not exist.'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(f'{type(e).__name__}: {e}'))