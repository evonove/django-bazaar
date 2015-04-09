from __future__ import unicode_literals

from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.forms.util import ErrorList
from django.forms import forms
from django.http import HttpResponseNotFound
from django.http.response import HttpResponseForbidden
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views import generic
from rest_framework import permissions

from braces.views import LoginRequiredMixin
from rest_framework import mixins
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import GenericViewSet

from ..goods.models import Product
from ..listings.seralizers import ListingSerializer
from ..settings import bazaar_settings
from .forms import ListingForm, PublishingForm
from .models import Listing, Publishing
from .stores import stores_loader
from ..mixins import BazaarPrefixMixin, FilterMixin, FilterSortableListView


class ListingListView(LoginRequiredMixin, BazaarPrefixMixin, FilterMixin, generic.ListView):
    model = Listing
    paginate_by = 50
    template_name = "bazaar/listings/listing_list.html"
    filter_name = "listing_filter"

    filter_class = bazaar_settings.LISTING_FILTER

    def get_queryset(self):
        qs = super(ListingListView, self).get_queryset()
        # prefetch list of values, populated by inherit items, plus items from each store
        prefetch_list = ["publishings__store"]
        for manager in stores_loader.get_all_store_managers():
            prefetch_list.extend(manager.get_store_extra("prefetch_list"))
        return qs.prefetch_related(*prefetch_list)

    def get_context_data(self, **kwargs):
        context = super(ListingListView, self).get_context_data(**kwargs)

        # populate forms and actions (tasks).
        tasks = []
        forms = []
        for manager in stores_loader.get_all_store_managers():
            forms.extend(manager.get_store_forms())
            tasks.append((manager.get_store_name(), manager.get_store_actions()))
        context['tasks'] = tasks
        # from template create a menu for every store with title == store_name
        # add all forms to context
        for form in forms:
            context[form.name] = form.form

        return context


class ListingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Listing
    template_name = "bazaar/listings/listing_detail_view.html"


class ListingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Listing
    success_url = reverse_lazy("bazaar:listings-list")

    def delete(self, request, *args, **kwargs):

        listing = self.get_object()
        has_publishings = Publishing.objects.filter(listing=listing).exists()
        if has_publishings:
            return HttpResponseForbidden()

        return super(ListingDeleteView, self).delete(request, *args, **kwargs)


class ListingUpdateView(LoginRequiredMixin, generic.FormView):
    form_class = ListingForm
    template_name = "bazaar/listings/listing_form.html"
    listing_to_update = None
    error_response = None
    success_url = reverse_lazy("bazaar:listings-list")

    def get_context_data(self, **kwargs):
        context = super(ListingUpdateView, self).get_context_data(**kwargs)
        context["listing"] = self.listing_to_update
        return context

    def get(self, request, *args, **kwargs):
        get_result = super(ListingUpdateView, self).get(request, *args, **kwargs)
        return self.error_response or get_result

    def get_initial(self):
        # Populate ticks in BooleanFields
        initial = {}
        listing_id = self.kwargs.get("pk", None)
        if listing_id:
            try:
                self.listing_to_update = Listing.objects.get(pk=listing_id)
                if self.listing_to_update.product is not None:
                    initial["product"] = self.listing_to_update.product.id
                    if self.listing_to_update.product.sets.exists():
                        initial["quantity"] = int(self.listing_to_update.product.sets.first().quantity)
            except Listing.DoesNotExist:
                self.error_response = HttpResponseNotFound()
        return initial

    def get_success_url(self):
        return reverse_lazy("bazaar:listings-detail", kwargs={'pk': self.object.id})

    def _retrieve_product(self, form):
        product_id = form.clean_product()
        return Product.objects.get(id=product_id)

    def form_valid(self, form):
        """
        Even if it's a valid form, it's not possible edit/update the listing set when there are associated publishings
        """
        if self.listing_to_update:
            # Update Listing
            listing = Listing.objects.get(pk=self.listing_to_update.id)

            publishings_exist = Publishing.objects.select_related('listing')\
                .filter(listing__id=self.listing_to_update.id).exists()
        else:
            # Create listing
            listing = Listing.objects.create()
            publishings_exist = False

        product = self._retrieve_product(form)

        if publishings_exist and listing.product != product:
            errors = form._errors.setdefault(forms.NON_FIELD_ERRORS, ErrorList())
            errors.append(_("Updating listing is denied. It's not allowed update/edit listings"
                            " when it is associated at least to one publishing."))
            return self.form_invalid(form)
        listing.product = product
        self.object = listing
        listing.save()

        return super(ListingUpdateView, self).form_valid(form)


class PublishingTagsMixin(object):
        def get_context_data(self, **kwargs):
            # Call the base implementation first to get a context
            context = super(PublishingTagsMixin, self).get_context_data(**kwargs)
            context['PUBLISHING_STATUS_CHOICES'] = dict(Publishing.PUBLISHING_STATUS_CHOICES)
            return context


class PublishingListView(LoginRequiredMixin, PublishingTagsMixin, FilterSortableListView):
    template_name = 'bazaar/listings/publishing_list.html'
    model = Publishing
    paginate_by = 100
    sort_fields = (
        'external_id', 'id', 'last_modified',
        'pub_date', 'status', 'store__name', 'is_active', 'title'
    )


class PublishingCreateView(SuccessMessageMixin, LoginRequiredMixin, PublishingTagsMixin, generic.CreateView):
    model = Publishing
    form_class = PublishingForm
    success_url = reverse_lazy("bazaar:publishings-list")
    template_name = 'bazaar/listings/publishing_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.last_modified = timezone.now()
        self.object.save()
        self.success_url = reverse_lazy("publishings-update", kwargs={'pk': self.object.id})
        return super(PublishingCreateView, self).form_valid(form)


class PublishingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Publishing
    success_url = reverse_lazy("bazaar:publishings-list")


class PublishingUpdateView(SuccessMessageMixin, LoginRequiredMixin, PublishingTagsMixin, generic.UpdateView):
    model = Publishing
    form_class = PublishingForm
    template_name = 'bazaar/listings/publishing_form.html'

    def get_success_url(self):
        return reverse_lazy("bazaar:publishings-update", kwargs={'pk': self.object.id})


class ListingViewSet(mixins.ListModelMixin, GenericViewSet):
    model = Listing
    serializer_class = ListingSerializer
    paginate_by = 10
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('product__name', )
