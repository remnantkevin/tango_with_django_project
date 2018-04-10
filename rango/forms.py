from django import forms
from rango.models import Category, Page

#? How does it know which fields link up whith which fields of the model? Answer: Order
#? How label input? e.g. Name:
#? How style errors etc.?

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")

    # Note that we have set the widget to be hidden with the parameter setting
    # widget=forms.HiddenInput(), and then set the value to zero with initial=0.
    # This is one way to set the field to zero by default. And since the fields
    # will be hidden the user won’t be able to enter a value for these fields.
    #? What else can widget?
    views = forms.IntegerField(initial=12)
    likes = forms.IntegerField(initial=89)
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
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page

        # We need to specify which fields are included on the form, via fields,
        # or specify which fields are to be excluded, via exclude.
        # Some fields may allow NULL values, so we may not want to include them.
        # Here, we are hiding the foreign key.
        # fields = ('title', 'url', 'views')
        exclude = ('category',)
