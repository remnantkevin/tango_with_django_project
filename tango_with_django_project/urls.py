"""tango_with_django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rango import views

from django.core.urlresolvers import reverse
from django.shortcuts import render

from django.conf import settings
from django.conf.urls.static import static

# ---- DJANGO-REGISTRATION-REDUX ----
from registration.backends.simple.views import RegistrationView

# Create a new class that redirects the user to the index page, if they successfully register.
#? where should this go in a proper app?
class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return reverse('rango:add_profile')


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rango/', include('rango.urls')),
    url(r'^admin/', admin.site.urls),

    # The django-registration-redux package provides a number of different registration backends,
    # depending on your needs. For example you may want a two-step process, where user is sent a
    # confirmation email, and a verification link. Here we will be using the simple one-step registration
    # process, where a user sets up their account by entering in a username, email, and password, and is
    # automatically logged in.

    # The Django Registration Redux package provides the machinery for numerous functions. In the
    # registration.backend.simple.urls , it provides the following mappings:
    # - registration -> /accounts/register/
    # - registration complete -> /accounts/register/complete/
    # - login -> /accounts/login/
    # - logout -> /accounts/logout/
    # - password change -> /password/change/
    # - password reset -> /password/reset/
    # while in the registration.backends.default.urls it also provides the functions for activating the
    # account in a two stage process:
    # - activation complete (used in the two-step registration) -> activate/complete/
    # - activate (used if the account action fails) -> activate/<activation_key>/
    # - activation email (notifies the user an activation email has been sent out)
    #     - activation email body (a text file, that contains the activation email text)
    #     - activation email subject (a text file, that contains the subject line of the
    #       activation email)
    # Now the catch. While Django Registration Redux provides all this functionality, it does not provide
    # the templates because these tend to be application specific. So we need to create the templates
    # associated with each view.
    # ^accounts/ ^register/closed/$ [name='registration_disallowed']
    # ^accounts/ ^register/complete/$ [name='registration_complete']
    # ^accounts/ ^register/$ [name='registration_register']
    # ^accounts/ ^login/$ [name='auth_login']
    # ^accounts/ ^logout/$ [name='auth_logout']
    # ^accounts/ ^password/change/$ [name='auth_password_change']
    # ^accounts/ ^password/change/done/$ [name='auth_password_change_done']
    # ^accounts/ ^password/reset/$ [name='auth_password_reset']
    # ^accounts/ ^password/reset/complete/$ [name='auth_password_reset_complete']
    # ^accounts/ ^password/reset/done/$ [name='auth_password_reset_done']
    # ^accounts/ ^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$ [name='auth_password_reset_confirm']

    # This will allow for accounts/register to be matched before any other accounts/ URL. This allows
    # us to redirect accounts/register to our customised registration view.
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name="registration_register"),

    url(r'^accounts/', include('registration.backends.simple.urls')),  # notice no $


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
