from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# models jenna made
class Post(models.Model):
  image = models.ImageField(upload_to = "uploads/")
  #author = models.ManyToManyField(Club, on_delete = models.CASCADE)
  caption = RichTextField(("caption"), blank = True)
  posted_at = models.DateTimeField(("posted_at"), auto_now = True)
  class Meta:
    verbose_name = "post"

  def __str__(self):
    return self.caption


class Club(models.Model):
  club_name = models.CharField(("club_name"), max_length = 500)
  description = models.TextField(("description"))
  president_name = models.CharField(("president_name"), max_length = 500)
  president_email = models.EmailField(("president_email"), max_length = 100)
  advisor_name = models.CharField(("advisor_name"), max_length = 500)
  advisor_email = models.EmailField(("advisor_email"), max_length = 100)
  posts = models.ManyToManyField(Post, blank = True)
  class Meta:
    verbose_name = "club"

  @property
  def postlist(self):
    return list(self.posts.all())
  
  def __str__(self):
    return self.club_name


class Member(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, primary_key = True)
  clubs = models.ManyToManyField(Club)
  class Meta:
    verbose_name = "member"

  @property
  def clublist(self):
    return list(self.clubs.all())

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
      models.UniqueConstraint(fields=['slug'], name='unique_slug')
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