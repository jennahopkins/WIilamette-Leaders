from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
  help = 'Change username for an existing user.'

  def add_arguments(self, parser):
    parser.add_argument('username', nargs='?', help="Username to change; by default, it's the current username.")
  
  def _validate_username(self, username):
    valid_chars = 'abcdefghijklmnopqrstuvwxyz0123456789@.+-_'
    for char in username:
      if char.lower() not in valid_chars:
        return False

  def handle(self, *args, **options):
    try:
      user = User.objects.get(username=options['username'])
      username = input('New username: ')
      valid = self._validate_username(username)
      if not valid:
        self.stderr.write(self.style.ERROR('Error: Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'))
      elif len(username) > 0:
        user.username = username
        user.save()
        self.stdout.write(self.style.SUCCESS('Username changed.'))
      else:
        self.stderr.write(self.style.ERROR('You must provide a username.'))
    except IntegrityError:
      self.stderr.write(self.style.ERROR('This username is already in use.'))
    except User.DoesNotExist:
      self.stderr.write(self.style.ERROR('This user does not exist.'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(f'{type(e).__name__}: {e}'))