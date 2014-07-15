from __future__ import unicode_literals
from django.conf.urls import patterns, url

from .views import ListingListView, ListingDetailView, ListingUpdateView, ListingDeleteView

urlpatterns = patterns(
    '',
    url(r'^listings/$', ListingListView.as_view(), name="listings-list"),
    url(r'^listings/new/$', ListingUpdateView.as_view(), name="listings-create"),
    url(r'^listings/(?P<pk>\d+)/$', ListingDetailView.as_view(), name='listings-detail'),
    url(r'^listings/update/(?P<pk>\d+)/$', ListingUpdateView.as_view(), name='listings-update'),
    url(r'^listings/delete/(?P<pk>\d+)/$', ListingDeleteView.as_view(), name='listings-delete'),

)