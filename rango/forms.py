from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from rango.models import Category, Page, UserProfile

#? How does it know which fields link up whith which fields of the model? Answer: Order
#? How label input? e.g. Name:
#? How style errors etc.?

# You’ll also notice that UserForm includes a definition of the password attribute. While a User model
# instance contains a password attribute by default, the rendered HTML form element will not hide
# the password. If a user types a password, the password will be visible. By updating the password
# attribute, we can specify that the CharField instance should hide a user’s input from prying eyes
# through use of the PasswordInput() widget.
#! This is what Tango uses, and so it doesn't use validation for some reason.
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

# For the user field within UserProfile model, we will need to make this
# association when we register the user. This is because when we create a
# UserProfile instance, we won’t yet have the User instance to refer to.
class UserProfileForm(forms.ModelForm):
    website = forms.URLField(required=False)
    picture = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ('website', 'picture')  # or fields = exclude('user',)


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")

    # Note that we have set the widget to be hidden with the parameter setting
    # widget=forms.HiddenInput(), and then set the value to zero with initial=0.
    # This is one way to set the field to zero by default. And since the fields
    # will be hidden the user won’t be able to enter a value for these fields.
    #? What else can widget?
    views = forms.IntegerField(widget=forms.HiddenInput(),initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(),initial=0)
    slug = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    # Inline class to provide additional information  on the form.
    # Creating a ModelForm without either the 'fields' attribute or the 'exclude' attribute is prohibited.
    class Meta:
        # Provide an association between the ModelForm and a model.
        model = Category
        # fields = ('name', 'views', 'likes', 'slug')  #? why no views, likes, slug? Don't need hidden if your model takes care of defaults
        # fields = ('name','likes','views') # doesn't save to DB unless linked here; links with form field in order
        # fields = ('name', 'views', 'likes')
        fields = ('name',)


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Title:")
    url = forms.URLField(max_length=200, help_text="URL:")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page

        # We need to specify which fields are included on the form, via fields,
        # or specify which fields are to be excluded, via exclude.
        # Some fields may allow NULL values, so we may not want to include them.
        # Here, we are hiding the foreign key.
        # fields = ('title', 'url', 'views')
        exclude = ('category',)

    def clean(self):
        #? Don't I have to call super here and run the clean method on the parent or does this happen by default?
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = "http://" + url
            cleaned_data['url'] = url

        return cleaned_data
