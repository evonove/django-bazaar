from django.core.urlresolvers import reverse
from django.contrib.auth.views import login as auth_login
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView


def login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("bazaar:home"))
    else:
        return auth_login(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = "home.html"
