from django.conf.urls import patterns, url

from .views import ProductListView, ProductCreateView

urlpatterns = patterns(
    '',
    url(r'^products/$', ProductListView.as_view(), name="product-list"),
    url(r'^products/new/$', ProductCreateView.as_view(), name="product-create"),
)