from django.shortcuts import render  # helper/shortcut function -> takes data and brings it together with the template to produce a complete HTML page that is retruned with an HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponse

from rango.models import Category, Page
from rango.forms import CategoryForm

#? How pass params? and then go if params['cat']

def index(request):
    # return HttpResponse("Rango says hey there partner!<br /><a href='/rango/about'>About</a>")
    # context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    # return render(request, 'rango/index.html', context=context_dict)  # template context is a dict that maps template variable names (boldmessage) to Python variables ('Crunchy...')

    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]

    # Top 5 most viewed pages.
    pages_list = Page.objects.order_by('-views')[:5]

    context_dict = {
        'categories': category_list,
        'pages': pages_list
    }

    return render(request, 'rango/index.html', context_dict)


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)
        # Why not?: pages = category.pages_set()

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


# The add_category() view function can handle three different scenarios:
# - showing a new, blank form for adding a category;
# - saving form data provided by the user to the associated model, and rendering the Rango homepage; and
# - if there are errors, redisplay the form with error messages.
def add_category(request):
    form = CategoryForm()

    # Check if the HTTP request was a POST i.e. if the user submitted data via the form
    if request.method == 'POST':
        form = CategoryForm(request.POST)  #? what is stored in request.POST? json? name=value?

        # Have we been provided with a vlaid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)  # can get ref by cat = form.save()

            # Now that the category is saved, we could give a confirmation message.
            # But since the most recent category added is on the index page then
            # we can direct the user back to the index page.
            # return index(request)  #! doesn't change url
            return redirect('index')  #? how use ref cat to then print on index? how pass ref not as regex param but ?= param?
        else:
            # The supplied form contained errors - print them to terminal.
            print(form.errors)

    # Will handle the bad form, new form, or no form data supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def about(request):
    return render(request, "rango/about.html")
