from __future__ import absolute_import
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import SortedDict
from django.views import generic

from braces.views import LoginRequiredMixin
from .filters import ProductFilter
from .forms import ProductForm
from .models import Product
from ..warehouse.models import Location
from ..mixins import BazaarPrefixMixin, FilterSortableListView


class ProductListView(LoginRequiredMixin, BazaarPrefixMixin, FilterSortableListView):
    model = Product
    paginate_by = 20
    filter_class = ProductFilter
    sort_fields = ('name', 'price', 'purchase_price', 'stock')

    def get_queryset(self):
        qs = super(ProductListView, self).get_queryset()
        location_storage = Location.objects.get_or_create(type=Location.LOCATION_STORAGE)[0]
        qs = qs.extra(
            select=SortedDict([
                ("stock",
                 "SELECT SUM(quantity) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND warehouse_stock.location_id = %s"),
                ("purchase_price",
                 "SELECT SUM(unit_price) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND warehouse_stock.location_id = %s"),
            ]),
            select_params=(
                location_storage.id,
                location_storage.id,
            )
        )
        return qs


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
