from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# By default, all models have an auto-increment integer field called id which is automatically assigned and acts a primary key.

# It may have been tempting to add the additional fields defined above by inheriting from the
# User model directly. However, because other applications may also want access to the User
# model, it not recommended to use inheritance, but to instead use a one-to-one relationship
# within your database.
class UserProfile(models.Model):
    user = models.OneToOneField(User)  # This line is required - links UserProfile to a User model instance.

    website = models.URLField(blank=True)  # blank=True: This allows each of the fields to be blank if necessary, meaning that users do not have to supply values for the attributes.
    # The value of the upload_to attribute is conjoined with the project’s
    # MEDIA_ROOT setting to provide a path with which uploaded profile images
    # will be stored.
    # The Django ImageField field makes use of the Python Imaging Library (PIL). If you have
    # not done so already, install PIL via Pip with the command pip install pillow .
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    # We override the save() method of the Category model, in which we will call the slugify
    # method and update the slug field with it. Note that every time the category name changes, the slug
    # will also change.
    # ?!
    # OverIQ does this in the Form
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)  #? how does calling the super class' save method work in terms of us overwriting the save method here
        #? if this is equivalent to model.Model.save(*args, **kwargs)...then how does Model know *which* instance (i.e. self) it is running save() on?
            # A: its not equivalent to that. The following are all equivalent:
            # - super().save(args, kwargs): I want to access the save method from my parent class, so explicitly pass in me (self) to my parent's method
            # - super(Category, self).save(args, kwargs)
            # - models.Model.save(self, args, kwargs)
        # Note: instance methods must be checking what calls them: if its of class type, then don't implicitly pass it in as first positional arg; else pass it (the object; not of class type) in implicitly as first positional arg.

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
