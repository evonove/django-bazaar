from __future__ import unicode_literals
from django.conf.urls import patterns, url

from .views import ListingListView, ListingDetailView, ListingUpdateView, ListingDeleteView, PublishingListView, \
    PublishingCreateView, PublishingUpdateView, PublishingDeleteView

urlpatterns = patterns(
    '',
    url(r'^listings/$', ListingListView.as_view(), name="listings-list"),
    url(r'^listings/new/$', ListingUpdateView.as_view(), name="listings-create"),
    url(r'^listings/(?P<pk>\d+)/$', ListingDetailView.as_view(), name='listings-detail'),
    url(r'^listings/update/(?P<pk>\d+)/$', ListingUpdateView.as_view(), name='listings-update'),
    url(r'^listings/delete/(?P<pk>\d+)/$', ListingDeleteView.as_view(), name='listings-delete'),

    # Publishing view
    url(r'^publishings/$', PublishingListView.as_view(), name="publishings-list"),
    url(r'^publishings/new/$', PublishingCreateView.as_view(), name="publishings-create"),
    url(r'^publishings/update/(?P<pk>\d+)/$', PublishingUpdateView.as_view(), name='publishings-update'),
    url(r'^publishings/delete/(?P<pk>\d+)/$', PublishingDeleteView.as_view(), name='publishings-delete'),

)