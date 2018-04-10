from django.db import models
from django.template.defaultfilters import slugify

# By default, all models have an auto-increment integer field called id which is automatically assigned and acts a primary key.

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    # We override the save() method of the Category model, in which we will call the slugify
    # method and update the slug field with it. Note that every time the category name changes, the slug
    # will also change.
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
