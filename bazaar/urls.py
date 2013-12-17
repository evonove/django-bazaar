from django.conf.urls import patterns, url, include

from .views import HomeView, MessagesView


bazaar_patterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^accounts/login/$', 'bazaar.views.login', name="login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name="logout"),

    # messages
    url(r'^messages/$', MessagesView.as_view(), name="messages"),
    url(r'^api/messages/', include("stored_messages.urls")),

    url(r'', include("bazaar.goods.urls")),
    url(r'', include("bazaar.listings.urls")),
)

# uniform namespace for all urls
urlpatterns = patterns(
    '',
    url(r'', include(bazaar_patterns, namespace="bazaar", app_name="bazaar")),
)
