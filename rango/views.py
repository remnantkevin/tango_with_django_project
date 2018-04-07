from django.shortcuts import render  # helper/shortcut function -> takes data and brings it together with the template to produce a complete HTML page that is retruned with an HttpResponse
from django.http import HttpResponse

from rango.models import Category, Page

def index(request):
    # return HttpResponse("Rango says hey there partner!<br /><a href='/rango/about'>About</a>")
    # context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    # return render(request, 'rango/index.html', context=context_dict)  # template context is a dict that maps template variable names (boldmessage) to Python variables ('Crunchy...')

    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    return render(request, 'rango/index.html', context_dict)

def details(request, ):
    return render(request, )

def about(request):
    return render(request, "rango/about.html")
