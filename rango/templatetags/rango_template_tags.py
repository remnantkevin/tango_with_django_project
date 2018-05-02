from django import template
from rango.models import Category

register = template.Library()

@register.inclusion_tag('rango/cats.html')  #? what if you want it to  be available across multiple templates?
def get_category_list(cat=None):
    return {
        'cats': Category.objects.all(),
        'act_cat': cat,
    }
