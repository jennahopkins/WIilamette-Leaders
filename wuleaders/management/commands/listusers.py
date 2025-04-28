"""
listusers.py
Provides a command to be used in the terminal to list all existing users of the app

Last edited:
4.27.25 by Jenna - provide additional documentation comments
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
  """
  Class to provide a command to be used in the terminal to list all existing users

  Variables:
    help: str to help describe class function
  """ 
  help = 'Returns a list of users.'

  def handle(self, *args, **options):
    """
    Main function ran when command used; iterates through the users and prints to terminal users and superusers

    Inputs:
      *args and **options: provides places for additional arguments to be passed into the function, by single or dictionary respectively
    
    Outputs:
      prints to the terminal all the users and superusers or error messages
    """
    try:
      # get all users and print each one and if they're a superuser or user
      users = User.objects.all()
      if len(users) > 0:
        for user in users:
          if user.is_superuser:
            print(f'(superuser) {user.username}')
          else:
            print(f'(user)      {user.username}')
      # there are no users
      else:
        self.stderr.write(self.style.ERROR('There are no users.'))
    # any exception occurs; print it to user
    except Exception as e:
      self.stderr.write(self.style.ERROR(e))