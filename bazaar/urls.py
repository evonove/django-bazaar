from django.conf.urls import patterns, url, include

from .views import HomeView


bazaar_patterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'', include("bazaar.goods.urls")),
)

# uniform namespace for all urls
urlpatterns = patterns(
    '',
    url(r'', include(bazaar_patterns, namespace="bazaar", app_name="bazaar"))
)
