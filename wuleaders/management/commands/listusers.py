from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
  help = 'Returns a list of users.'

  def handle(self, *args, **options):
    try:
      users = User.objects.all()
      if len(users) > 0:
        for user in users:
          if user.is_superuser:
            print(f'(superuser) {user.username}')
          else:
            print(f'(user)      {user.username}')
      else:
        self.stderr.write(self.style.ERROR('There are no users.'))
    except Exception as e:
      self.stderr.write(self.style.ERROR(e))