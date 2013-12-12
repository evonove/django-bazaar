from django.views import generic

from braces.views import LoginRequiredMixin

from ..mixins import BazaarPrefixMixin, FilterMixin
from .filters import ListingFilter
from .models import Listing


class ListingListView(LoginRequiredMixin, BazaarPrefixMixin, FilterMixin, generic.ListView):
    model = Listing
    paginate_by = 50

    filter_class = ListingFilter
