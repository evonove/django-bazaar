from __future__ import absolute_import
from __future__ import unicode_literals
from django.core.urlresolvers import reverse_lazy

from django.views import generic

from braces.views import LoginRequiredMixin
from bazaar.goods.filters import ProductFilter
from bazaar.goods.forms import ProductForm

from ..mixins import BazaarPrefixMixin, FilterSortableListView
from .models import Product


class ProductListView(LoginRequiredMixin, BazaarPrefixMixin, FilterSortableListView):
    model = Product
    paginate_by = 20
    fields = ['photo', 'name', 'price', 'ean']
    filter_class = ProductFilter
    sort_fields = ('name', 'price', 'cost', 'stock')


class ProductDetailView(LoginRequiredMixin, BazaarPrefixMixin, generic.DetailView):
    model = Product
    fields = ['photo', 'name', 'description', 'ean', 'quantity', 'price', 'cost']


class ProductCreateView(LoginRequiredMixin, BazaarPrefixMixin, generic.CreateView):
    model = Product
    form_class = ProductForm

    fields = ['name', 'description', 'ean', 'photo', 'price']

    def get_success_url(self):
        return reverse_lazy("bazaar:product-detail", kwargs={'pk': self.object.id})


class ProductDeleteView(LoginRequiredMixin, BazaarPrefixMixin, generic.DeleteView):
    model = Product
    success_url = reverse_lazy('bazaar:product-list')


class ProductUpdateView(LoginRequiredMixin, BazaarPrefixMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy("bazaar:product-detail", kwargs={'pk': self.object.id})
