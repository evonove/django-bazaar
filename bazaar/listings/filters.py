from __future__ import unicode_literals

from django import forms

import django_filters

from ..filters import BaseFilterSet
from .models import Listing


class LowStockListingFilter(django_filters.Filter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(pk__in=Listing.objects.low_stock_ids())

        return qs


class LowPriceListingFilter(django_filters.Filter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(pk__in=Listing.objects.low_cost_ids())
        return qs


class ListingFilter(BaseFilterSet):
    title = django_filters.CharFilter(lookup_type="icontains")
    available_units = django_filters.NumberFilter(name="publishings__available_units",
                                                  lookup_type="lte")
    low_stock = LowStockListingFilter()
    low_price = LowPriceListingFilter()

    class Meta:
        model = Listing
        fields = ["title", "publishings__store", "available_units"]
