from django.conf.urls import patterns, url, include

from .views import HomeView


urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'', include("bazaar.goods.urls", namespace="bazaar")),
)
