from __future__ import unicode_literals

from django import forms

import django_filters

from ..filters import BaseFilterSet
from .models import Listing, Publishing


class HighAvailabilityListingFilter(django_filters.Filter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(pk__in=Listing.objects.high_availability())

        return qs


class UnavailableListingFilter(django_filters.Filter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(pk__in=Listing.objects.low_availability())

        return qs


class AvailableUnitsFilter(django_filters.Filter):
    field_class = forms.DecimalField

    def filter(self, qs, value):

        if value is not None:
            qs = qs.filter(publishings__in=Publishing.objects.main_publishings().filter(available_units__lte=value))

        return qs


class LowPriceListingFilter(django_filters.Filter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(pk__in=Listing.objects.low_price())
        return qs


class ListingFilter(BaseFilterSet):
    title = django_filters.CharFilter(lookup_type="icontains")
    available_units = AvailableUnitsFilter()
    unavailable = UnavailableListingFilter()
    low_price = LowPriceListingFilter()
    high_availability = HighAvailabilityListingFilter()

    class Meta:
        model = Listing
        fields = ["publishings__title", "publishings__store", "available_units"]
