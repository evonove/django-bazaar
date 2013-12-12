from __future__ import unicode_literals

import django_filters

from .models import Listing


class ListingFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Listing
        fields = ['title', "publishings__store", "publishings__available_units"]
