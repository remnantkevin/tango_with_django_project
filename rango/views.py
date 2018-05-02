from django.shortcuts import render  # helper/shortcut function -> takes data and brings it together with the template to produce a complete HTML page that is retruned with an HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm, UserForm
from rango.forms import UserCreateForm

from datetime import datetime

from rango.webhose_search import run_query

#? Q: How pass params? and then go if params['cat'] | A: request.GET.
#? Q: how do you restrict to only those user NOT logged in, i.e. for the registration page? (although maybe you still allow it -- could register another account).
#? Q: When redirected to login, way to check where you've just been redirected fron? besides a ?=parameter ? in cookie/session data? that would override where it wants to defaultly send you.
#           seems to have this as a ?next= param automatiicaly, but login success reponse overrides
#? Q: how does django template engine handle non-existing objects: e.g. login_failure in user_login()? [seems it doesn't throw error like python]

def register(request):
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST request, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)  #? is data the first positional argument in ModelForm?
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save user form  data to the database
            # #? Q: how is password stored at this point if it's only hashed in next, next line? in what form is it transferred over the internet? | A: needs to be transferred over https
            user = user_form.save(commit=False)  # commiting here would save the unhashed password into the db.
            # Now we hash the password with the set_password method.
            user.set_password(user.password)
            # Once hashed, we can update out user object (in the db).
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems (not having a User object for a UserProfile).
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile instance.
            profile.save()

            # Update our variable to indicate that the registration was successfull.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print errors to the console.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST request, so we render our form using two ModelForm instances.
        # Forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
        'rango/register.html',
        {
            'registered': registered,
            'user_form': user_form,
            'profile_form': profile_form
        }
    )


# Remember, once a newly registered user hits this view, they will have had a new account
# created for them - so we can safely assume that he or she is now logged into Rango.
@login_required
def add_profile(request):
    profile_form = UserProfileForm()

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('rango:index')
        else:
            print(profile_form.errors)  #! should do more substantial handling
    # If GET request, if unknown request, if POST request and not valid form data
    return render(request, 'rango/add_profile.html', {'profile_form': profile_form})


@login_required
def profile(request, username):
    try:
        selecteduser = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('rango:index')

    userprofile = UserProfile.objects.get_or_create(user=selecteduser)[0]  # user may not have created a profile yet
    profile_form = UserProfileForm({
        'website': userprofile.website,
        'picture': userprofile.picture  # this doesn't 'fill' the picture selector form element
    })  #? how populate with profile data? i.e. website? give it the userprofile object? |A: need to give dictionary, like the key0value paits it would get from request.POST

    if request.method == 'POST':  #? you could also check that username == request.user here...overkill?
        # We then extract information from the form into a UserProfileForm
        # instance that is able to reference to the UserProfile model instance
        # that it is saving to, rather than. Creating a new UserProfile instance
        # each time. Remember, we are updating, not creating new.
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)  #UPDATING
        if profile_form.is_valid():
            profile_form.save(commit=True)  # UPDATING:  updates userprofile UserProfile instance instead of creating a new UserProfile instance
            # print("url:", reverse('rango:profile', kwargs={'username':username}))
            return redirect('rango:profile', username)  #! can use this or redirect and reverse (see below)
            # return redirect(reverse('rango:profile', kwargs={'username':username}))
        else:
            print(profile_form.errors)

    return render(request, 'rango/profile.html', {
        'form': profile_form,
        'selecteduser': selecteduser,
        'userprofile': userprofile
    })


@login_required
def list_profiles(request):
    user_profile_list = UserProfile.objects.all()
    # for profile in user_profile_list:
    #     if profile.picture.name:
    #         print(profile.picture.name)
    return render(request, 'rango/list_profiles.html', {'userprofile_list': user_profile_list})


def user_login(request):
    #? What about the form? | A: creating our own html form
    # If the request is POST, try and pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("uname: {} | psswd: {}".format(username, password))

        # Use Django to attempt to see if the username/password combination
        # is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        print(user)

        # If we have a User object stored in user, the login details provided
        # are correct.
        # If None, no matching user was found.
        if user:
            # Check if account is active - may have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # Send the user back to the home page.
                login(request, user)  #?
                return HttpResponseRedirect(reverse('index'))  #? diff to redirect?
            else:
                # An inactive account was used - no logging in.
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided, so we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return render(request, 'rango/login.html', {'login_failure': True})
    # The request is not POST, so display the login form.
    else:
        # No context variables to pass to the template, hence the empty dictionary.
        return render(request, 'rango/login.html', {})


# Only those users who are logged in should be able to logout.
@login_required
def user_logout(request):
    # At this point we know that the user is logged in, so log them out.
    logout(request)
    # Once logged out, send the user back to the homepage.
    return HttpResponseRedirect(reverse('index'))


@login_required
def restricted(request):
    # request.session.clear()
    return render(request, 'rango/restricted.html')


def index(request):
    # request.session.set_test_cookie()
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

    # response = render(request, 'rango/index.html', context_dict)

    # visitor_cookie_handler(request, response)
    visitor_cookie_handler(request)  #? decorator?

    # context_dict['visits'] = request.session['visits']

    return render(request, 'rango/index.html', context_dict)


# COOKIE VERSION
#   visitor_cookie_handler(request, response)
#   This helper function takes in the request and response objects - because we want
#   to be able to access the incoming cookies from the request, and add or update
#   cookies in the response.
#?  we get from request and change on response, but when does response tell the next request that the value has changed? | A: the response edits the cookie file and the request reads from the cookie file.
#!       but -- see template -- you can't access the response objects value, so you'll be 1 count behind
def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # visits = int(request.COOKIES.get('visits', '1'))
    visits = int(request.session.get('visits', '1'))

    last_visit_cookie = request.session.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (last_visit_time - datetime.now()).seconds > 0:  # timedelta object
        visits += 1
        # set_cookie sets a cookie
        # response.set_cookie('last_visit', datetime.now())  # automatically cast to a string
        request.session['last_visit'] = str(datetime.now())
    else:
        # response.set_cookie('last_visit', last_visit_cookie)
        request.session['last_visit'] = las_visit_cookie

    # response.set_cookie('visits', visits)
    request.session['visits'] = visits


def show_category(request, category_name_slug):

    context_dict = {}

    if request.method == 'POST':
        results = []

        query_string = request.POST.get('query', None)
        if query_string:  # isn't blank
            query_string = query_string.strip()
            results = run_query(query_string)

        context_dict.update({'result_list': results, 'query': query_string})


    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category).order_by('-views')
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
@login_required
def add_category(request):
    form = CategoryForm()

    # Check if the HTTP request was a POST i.e. if the user submitted data via the form
    if request.method == 'POST':
         #? what is stored in request.POST? json? name=value?
        # <QueryDict: {'csrfmiddlewaretoken': ['dAfxWkD5zfR1xtLpnct2QA4KJmDPitezEL0HIS0LRMQBYCJM4XKV51kAYquruXvw'], 'slug': [''], 'name': ['Hello there'], 'views': ['12'], 'likes': ['89'], 'submit': ['Create Category']}>
        form = CategoryForm(request.POST)

        # Have we been provided with a vlaid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)  # can get ref by cat = form.save(); form.save() creates a new Catgeory and returns it; commit=True means it must also save it to the DB

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

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page_new = form.save(commit=False)  # create new Page, don't save it to the DB, return this new page
                page_new.category = category
                page_new.views = 0
                page_new.save()
            return show_category(request, category_name_slug)
        # else:
        #     print(form.errors)

    return render(request, 'rango/add_page.html', {'form': form, 'category': category})


@login_required
def add_page_to_category(request):
    context = {}
    if request.method == 'GET':
        cat_slug = request.GET.get('slug', None)

        if cat_slug:
            page_title = request.GET.get('title', None)
            page_url = request.GET.get('url', None)

            try:
                category = Category.objects.get(slug=cat_slug)
            except Category.DoesNotExist:
                pass
            else:
                Page.objects.get_or_create(category=category, title=page_title, url=page_url)[0]  # creates and saves, is that what create does? Yes, create instantiates and saves.
                # page.url = page_url
                # page.save()

                # context['category'] = category
                context['pages'] = category.page_set.order_by('-views')

    return render(request, 'rango/page_list.html', context)

def search(request):
    results = []

    if request.method == 'POST':
        query_string = request.POST['query'].strip()
        if query_string:  # isn't blank
            results = run_query(query_string)

    return render(request, 'rango/search.html', {'result_list': results, 'query': query_string})


def goto(request):
    if request.method == 'GET':
        if 'page_id' in request.GET:
            try:
                page_id = int(request.GET['page_id'])
                page = Page.objects.get(pk=page_id)
                page.views += 1
                page.save()
                # page id found and views increased by 1
                return redirect(page.url)
            except:
                # page_id param not an int, page if not found
                pass
    # Not GET request, no page_id param provided
    return redirect(reverse('rango:index'))


def about(request):

    # print("test cookie value: {}".format(request.session.TEST_COOKIE_VALUE))
    # print("test cookie name: {}".format(request.session.TEST_COOKIE_NAME))
    print(type(request.session))
    print(request.session)
    print(dir(request.session))
    print(request.session.__dict__)
    #
    # if request.session.test_cookie_worked():
    #     print("TEST COOKIE WORKED")
    #     request.session.delete_test_cookie()

    print(request.method)
    print(request.user.__dict__)
    # print("session: {}".format(dir(request.session)))

    context = {'visits': request.session.get('visits')}

    return render(request, "rango/about.html", {})

#? what happens with this whol ajax call if not logged in?
@login_required
def like_category(request):
    # could check whether user has liked before
    try:
        catid = request.GET.get('category_id', None)
        cat = Category.objects.get(pk=catid)
    except Category.DoesNotExist:
        return HttpResponse(0)

    cat.likes += 1
    cat.save()

    return HttpResponse(cat.likes)

def get_category_list(max_results=0, starts_with=''):
    categories = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        categories = categories[:max_results]
    return categories

def suggest_category(request):
    # categories = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['query']

    categories = get_category_list(max_results=8, starts_with=starts_with)

    return render(request, 'rango/cats.html', {'cats': categories})
