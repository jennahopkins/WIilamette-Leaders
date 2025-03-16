from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

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