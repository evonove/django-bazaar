from __future__ import unicode_literals

from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import logout as auth_logout
from django.contrib.sites.models import get_current_site
from django.http.response import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from stored_messages.models import Inbox

from .settings import bazaar_settings


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='bazaar/registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """

    # Ensure the user-originating redirection url is safe.
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = resolve_url(bazaar_settings.LOGIN_REDIRECT_URL)

    if request.user.is_authenticated():
        return HttpResponseRedirect(redirect_to)

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def logout(request, *args, **kwargs):
    return auth_logout(request, template_name='bazaar/registration/logged_out.html',
                       *args, **kwargs)


class HomeView(TemplateView):
    template_name = "home.html"


class MessagesView(ListView):
    model = Inbox
    paginate_by = 10
    template_name = "bazaar/inbox_list.html"

    def get_queryset(self):
        qs = super(MessagesView, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs.select_related("message").order_by("-message__date")
