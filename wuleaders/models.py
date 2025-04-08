from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# models jenna made

class Club(models.Model):
  club_name = models.CharField(("club_name"), max_length = 500)
  description = models.TextField(("description"))
  president_name = models.CharField(("president_name"), max_length = 500)
  president_email = models.EmailField(("president_email"), max_length = 100)
  advisor_name = models.CharField(("advisor_name"), max_length = 500)
  advisor_email = models.EmailField(("advisor_email"), max_length = 100)
  slug = models.CharField(("slug"), max_length=250)
  photo = models.ImageField(upload_to = "uploads/", blank = True)
  class Meta:
    verbose_name = "club"
    constraints = [
      models.UniqueConstraint(fields=['slug'], name='club_unique_slug')
    ]

  @property
  def postlist(self):
    postlist = list(self.posts.all())
    #order_by('created_at').reverse()
    return sorted(postlist, key = lambda post: post.posted_at, reverse = True)

  @property
  def memberlist(self):
    rolelist = list(self.role.all())
    member_roles = list(filter(lambda _role: _role.role != "Follower", rolelist))
    members = []
    for _role in member_roles:
      members += _role.memberlist
    return members

  @property
  def roledict(self):
    roledict = {}
    rolelist = list(self.role.all())
    for role in rolelist:
      roledict[role] = role.memberlist
    return roledict

  @property
  def editors(self):
    rolelist = list(self.role.all())
    edit_roles = list(filter(lambda _role: _role.can_edit == True, rolelist))
    editors = []
    for _role in edit_roles:
      editors += _role.memberlist
    return editors

  @property
  def followers(self):
    rolelist = list(self.role.all())
    follow_roles = list(filter(lambda _role: _role.role == "Follower", rolelist))
    followers = []
    for _role in follow_roles:
      followers += _role.memberlist
    return followers

  
  def __str__(self):
    return self.club_name


class Post(models.Model):
  image = models.ImageField(upload_to = "uploads/", blank = True)
  caption = RichTextField(("caption"))
  posted_at = models.DateTimeField(("posted_at"), auto_now = True)
  authors = models.ManyToManyField(Club, related_name = "posts", blank = True)
  class Meta:
    verbose_name = "post"

  @property
  def authorlist(self):
    authors = self.authors.all()
    for author in authors:
      yield author

  def __str__(self):
    return self.caption


class Role(models.Model):
  club = models.ForeignKey(Club, related_name = "role", on_delete = models.CASCADE)
  role = models.CharField(("role"), max_length = 100)
  can_edit = models.BooleanField(("can_edit"), default = False)

  @property
  def memberlist(self):
    return list(self.member.all())

  def member(self):
    return self.member

  def __str__(self):
    return self.role


class Member(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, primary_key = True)
  clubs = models.ManyToManyField(Club, blank = True, related_name = "member")
  roles = models.ManyToManyField(Role, blank = True, related_name = "member")
  photo = models.ImageField(upload_to = "uploads/", blank = True)
  pronouns = models.CharField(("pronouns"), max_length = 50, blank = True) 
  class Meta:
    verbose_name = "member"

  @property
  def clublist(self):
    return list(self.clubs.all())

  @property
  def roleslist(self):
    return list(self.roles.all())

  @property
  def name(self):
    return self.user.first_name + " " + self.user.last_name

  @property
  def email(self):
    return self.user.email

  def __str__(self):
    return self.name






# Create your models here.
class Article(models.Model):
  title = RichTextField(('title'), blank=True)
  slug = models.CharField(("slug"), max_length=250)
  content = RichTextUploadingField(('content'), blank=True)
  views = models.IntegerField(("views"), default=0)
  created_at = models.DateTimeField(("created_at"), auto_now_add=True)
  updated_at = models.DateTimeField(("updated_at"), auto_now=True)
  class Meta:
    verbose_name = "article"
    verbose_name_plural = 'articles'
    constraints = [
      models.UniqueConstraint(fields=['slug'], name='article_unique_slug')
    ]
  
  def __str__(self):
      return self.slug
  

class Comment(models.Model):
  article = models.ForeignKey(Article, on_delete=models.CASCADE)
  content = models.TextField(("content"))
  created_at = models.DateTimeField(("created_at"), auto_now_add=True)
  class Meta:
    verbose_name = ("comment")
    verbose_name_plural = ("comments")

  def __str__(self):
      return self.content
  
class About(models.Model):
  title = RichTextUploadingField(('title'), blank=True)
  content = RichTextUploadingField(('content'), blank=True)
  class Meta:
    verbose_name = ("about")

  def __str__(self):
      return self.title