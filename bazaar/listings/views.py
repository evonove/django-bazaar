from django.views import generic

from braces.views import LoginRequiredMixin

from ..mixins import BazaarPrefixMixin
from .models import Listing


class ListingListView(LoginRequiredMixin, BazaarPrefixMixin, generic.ListView):
    model = Listing
    paginate_by = 20
