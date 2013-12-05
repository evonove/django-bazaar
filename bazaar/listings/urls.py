from django.conf.urls import patterns, url

from .views import ListingListView

urlpatterns = patterns(
    '',
    url(r'^listings/$', ListingListView.as_view(), name="listing-list"),
)