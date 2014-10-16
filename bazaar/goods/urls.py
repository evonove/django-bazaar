from __future__ import absolute_import
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import ProductListView, ProductCreateView, ProductDetailView


urlpatterns = patterns(
    '',
    url(r'^products/$', ProductListView.as_view(), name="product-list"),
    url(r'^products/new/$', ProductCreateView.as_view(), name="product-create"),
    url(r'^products/(?P<pk>\d+)/$', ProductDetailView.as_view(), name="product-detail")
)
