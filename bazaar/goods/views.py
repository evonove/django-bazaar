from __future__ import absolute_import
from __future__ import unicode_literals
from django.core.urlresolvers import reverse, reverse_lazy

from django.views import generic

from braces.views import LoginRequiredMixin

from ..mixins import BazaarPrefixMixin
from .models import Product


class ProductListView(LoginRequiredMixin, BazaarPrefixMixin, generic.ListView):
    model = Product
    paginate_by = 20
    fields = ['photo', 'name', 'price', 'ean']


class ProductDetailView(LoginRequiredMixin, BazaarPrefixMixin, generic.DetailView):
    model = Product
    fields = ['photo', 'name', 'description', 'ean', 'quantity', 'price', 'cost']


class ProductCreateView(LoginRequiredMixin, BazaarPrefixMixin, generic.CreateView):
    model = Product
    fields = ['name', 'description', 'ean', 'photo', 'price']


class ProductDeleteView(LoginRequiredMixin, BazaarPrefixMixin, generic.DeleteView):
    model = Product
    success_url = reverse_lazy('bazaar:product-list')


class ProductUpdateView(LoginRequiredMixin, BazaarPrefixMixin, generic.UpdateView):
    model = Product
    fields = ['name', 'description', 'ean', 'photo', 'price']