from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth.views import login as auth_login
from django.http.response import HttpResponseRedirect
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from stored_messages.models import Inbox


def login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("bazaar:home"))
    else:
        return auth_login(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = "home.html"


class MessagesView(ListView):
    model = Inbox
    paginate_by = 10
    template_name = "bazaar/inbox_list.html"

    def get_queryset(self):
        qs = super(MessagesView, self).get_queryset()
        return qs.select_related("message").order_by("-message__date")
