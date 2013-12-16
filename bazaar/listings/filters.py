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


class ListingFilter(BaseFilterSet):
    title = django_filters.CharFilter(lookup_type="icontains")
    low_stock = LowStockListingFilter()

    class Meta:
        model = Listing
        fields = ["title", "publishings__store", "publishings__available_units"]
