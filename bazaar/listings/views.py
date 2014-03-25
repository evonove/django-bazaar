from __future__ import unicode_literals

from django.views import generic

from braces.views import LoginRequiredMixin

from ..mixins import BazaarPrefixMixin, FilterMixin
from .filters import ListingFilter
from .models import Listing


class ListingListView(LoginRequiredMixin, BazaarPrefixMixin, FilterMixin, generic.ListView):
    model = Listing
    paginate_by = 50

    filter_class = ListingFilter

    def get_queryset(self):
        qs = super(ListingListView, self).get_queryset()
        #TODO location: listing_sets__product__stock
        return qs.prefetch_related("listing_sets__product", "publishings__store")
