"""
models.py
File that contains all models used in app; models are used to store information about clubs, members, roles, posts in database

Last edited:
4.27.25 by Jenna - added additional documentation comments
"""

from django.db import models
from django.conf import settings


class Club(models.Model):
  """
  Model that represents a Willamette club

  Fields:
    club_name: name of the club as appears on the Willamette website
    description: description of the club as appears on the Willamette website
    president_name: name of the president of the club as appears on the Willamette website
    president_email: email of the president of the club as appears on the Willamette website
    advisor_name: name of the advisor of the club as appears on the Willamette website
    advisor_email: email of the president of the club as appears on the Willamette website
    slug: website address slug of the club to distinguish it from others
    photo: profile picture of the club if they wish to upload one
  """
  club_name = models.CharField(("club_name"), max_length = 500)
  description = models.TextField(("description"))
  president_name = models.CharField(("president_name"), max_length = 500)
  president_email = models.EmailField(("president_email"), max_length = 100)
  advisor_name = models.CharField(("advisor_name"), max_length = 500)
  advisor_email = models.EmailField(("advisor_email"), max_length = 100)
  slug = models.CharField(("slug"), max_length=250)
  photo = models.ImageField(upload_to = "uploads/", blank = True)

  class Meta:
    """
    Extra information about the club
    """
    verbose_name = "club"
    # make sure every slug is unique so it doesn't get confused which one to display
    constraints = [
      models.UniqueConstraint(fields=['slug'], name='club_unique_slug')
    ]

  @property
  def postlist(self):
    """
    Provides a list of posts the club has made

    Inputs:
      None

    Outputs:
      list: Post objects the clubs has made
    """
    postlist = list(self.posts.all())
    return sorted(postlist, key = lambda post: post.posted_at, reverse = True)

  @property
  def memberlist(self):
    """
    Provides a list of members of the club

    Inputs:
      None

    Outputs:
      list: Member objects in the club
    """
    rolelist = list(self.role.all())
    member_roles = list(filter(lambda _role: _role.role != "Follower", rolelist))
    members = []
    for _role in member_roles:
      members += _role.memberlist
    return members

  @property
  def roledict(self):
    """
    Provides a dictionary of roles in the club and members with that role

    Inputs:
      None

    Outputs:
      dict: key = Role object that is related to the club; value = list of Member objects that hold that role
    """
    roledict = {}
    rolelist = list(self.role.all())
    for role in rolelist:
      roledict[role] = role.memberlist
    return roledict

  @property
  def editors(self):
    """
    Provides a list of members who have editing privileges in the club

    Inputs:
      None

    Outputs:
      list: Member objects that have editing privileges in the club
    """
    rolelist = list(self.role.all())
    edit_roles = list(filter(lambda _role: _role.can_edit == True, rolelist))
    editors = []
    for _role in edit_roles:
      editors += _role.memberlist
    return editors

  @property
  def followers(self):
    """
    Provides a list of followers of the club

    Inputs:
      None

    Outputs:
      list: Member objects that follow the club
    """
    rolelist = list(self.role.all())
    follow_roles = list(filter(lambda _role: _role.role == "Follower", rolelist))
    followers = []
    for _role in follow_roles:
      followers += _role.memberlist
    return followers

  
  def __str__(self):
    """
    Provides a string representation of the club

    Inputs:
      None

    Outputs:
      str: name of the club as appears on the Willamette website
    """
    return self.club_name


class Post(models.Model):
  """
  Model that represents a post a club can make

  Fields:
    image: picture associated with the post
    caption: caption text associated with the post
    posted_at: date and time when the post was made (pacific time)
    authors: the clubs that authored the post
  """
  image = models.ImageField(upload_to = "uploads/", blank = True)
  caption = models.TextField(("caption"))
  posted_at = models.DateTimeField(("posted_at"), auto_now_add = True)
  authors = models.ManyToManyField(Club, related_name = "posts", blank = True)
  
  class Meta:
    """
    Extra information about the post
    """
    verbose_name = "post"

  @property
  def authorlist(self):
    """
    Iterates through the authors of the club

    Inputs:
      None
    
    Outputs:
      Club: yields each Club object that authored the post
    """
    authors = self.authors.all()
    for author in authors:
      yield author

  def __str__(self):
    """
    Provides a string representation of the post

    Inputs:
      None

    Outputs:
      str: caption of the post
    """
    return self.caption


class Role(models.Model):
  """
  Model of the role a person has in a club

  Fields:
    club: Club object that the role is associated with
    role: name of the role that the person has
    can_edit: True if the person has editing privileges in the club, False if not
  """
  club = models.ForeignKey(Club, related_name = "role", on_delete = models.CASCADE)
  role = models.CharField(("role"), max_length = 100)
  can_edit = models.BooleanField(("can_edit"), default = False)

  @property
  def memberlist(self):
    """
    Provides a list of members that have this role

    Inputs:
      None

    Outputs:
      list: Member objects associated with this role
    """
    return list(self.member.all())

  def __str__(self):
    """
    Provides a string representation of the role

    Inputs:
      None
    
    Outputs:
      str: name of the role
    """
    return self.role


class Member(models.Model):
  """
  Model of a member of a club or user of the app

  Fields:
    user: User object associated with this member
    clubs: Club objects that the member is a part of
    roles: Role objects that the member contains in their clubs
    photo: profile picture of the member if they wish to upload one
    pronouns: pronouns of the member if they wish to upload them
  """
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, primary_key = True)
  clubs = models.ManyToManyField(Club, blank = True, related_name = "member")
  roles = models.ManyToManyField(Role, blank = True, related_name = "member")
  photo = models.ImageField(upload_to = "uploads/", blank = True)
  pronouns = models.CharField(("pronouns"), max_length = 50, blank = True) 

  class Meta:
    """
    Extra information about the member
    """
    verbose_name = "member"

  @property
  def clublist(self):
    """
    Provides a list of clubs the member is a part of

    Inputs:
      None

    Outputs:
      list: Club objects the member is a part of
    """
    return list(self.clubs.all())

  @property
  def roleslist(self):
    """
    Provides a list of roles the member holds

    Inputs:
      None

    Outputs:
      list: Role objects the member holds
    """
    return list(self.roles.all())

  @property
  def name(self):
    """
    Provides the full name of the member

    Inputs:
      None

    Outputs:
      str: the full name of the member
    """
    return self.user.first_name + " " + self.user.last_name

  @property
  def email(self):
    """
    Provides the email of the member

    Inputs:
      None

    Outputs:
      str: the email of the member
    """
    return self.user.email

  def __str__(self):
    """
    Provides a string representation of the member

    Inputs:
      None

    Outputs:
      str: full name of the member
    """
    return self.name




