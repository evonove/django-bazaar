from __future__ import unicode_literals

from django.views import generic

from braces.views import LoginRequiredMixin
from ..management.stores.config import stores_loader
from ..management.listings.config import listings_loader

from ..mixins import BazaarPrefixMixin, FilterMixin
from .models import Listing


class ListingListView(LoginRequiredMixin, BazaarPrefixMixin, FilterMixin, generic.ListView):
    model = Listing
    paginate_by = 50
    template_name = "bazaar/listings/listing_list.html"
    filter_name = "listing_filter"

    filter_class = listings_loader.get_listing_filter()

    def get_queryset(self):
        qs = super(ListingListView, self).get_queryset()
        #prefetch list of values, populated by inherit itmes, plus items from each store
        prefetch_list = ["listing_sets__product", "publishings__store"]
        for manager in stores_loader.get_all_store_managers():
            prefetch_list.extend(manager.get_store_extra("prefetch_list"))
        return qs.prefetch_related(*prefetch_list)

    def get_context_data(self, **kwargs):
        context = super(ListingListView, self).get_context_data(**kwargs)

        #populate forms and actions (tasks).
        tasks = []
        forms = []
        for manager in stores_loader.get_all_store_managers():
            forms.extend(manager.get_store_forms())
            tasks.append((manager.get_store_name(), manager.get_store_actions()))
        context['tasks'] = tasks
        #from template create a menu for every store with title == store_name
        #add all forms to context
        for form in forms:
            context[form.name] = form.form

        return context