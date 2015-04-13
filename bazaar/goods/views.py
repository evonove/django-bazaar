from __future__ import absolute_import
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.datastructures import SortedDict
from django.views import generic

from braces.views import LoginRequiredMixin
from bazaar.listings.models import Publishing
from bazaar.warehouse.locations import get_storage
from .filters import ProductFilter
from .forms import ProductForm, ProductSetFormSet, CompositeProductForm
from .models import Product, ProductSet
from ..mixins import BazaarPrefixMixin, FilterSortableListView


class ProductListView(LoginRequiredMixin, BazaarPrefixMixin, FilterSortableListView):
    model = Product
    paginate_by = 20
    filter_class = ProductFilter
    sort_fields = ('name', 'price', 'purchase_price', 'stock')

    def get_queryset(self):
        qs = super(ProductListView, self).get_queryset()
        location_storage = get_storage()
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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProductDetailView, self).get_context_data(**kwargs)

        # Check if this product was ever published
        product = self.get_object()
        ps = ProductSet.objects.filter(product=product)
        has_publishings = Publishing.objects.filter(listing__product=product).exists() or \
            Publishing.objects.filter(listing__product__in=[pset.composite for pset in ps]).exists()
        context['deletable'] = not has_publishings

        return context


class ProductCreateView(LoginRequiredMixin, BazaarPrefixMixin, generic.CreateView):
    model = Product
    form_class = ProductForm

    fields = ['name', 'description', 'ean', 'photo', 'price']

    def get_success_url(self):
        return reverse_lazy("bazaar:product-detail", kwargs={'pk': self.object.id})


class ProductDeleteView(LoginRequiredMixin, BazaarPrefixMixin, generic.DeleteView):
    model = Product
    success_url = reverse_lazy('bazaar:product-list')

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        ps = ProductSet.objects.filter(product=product)
        has_publishings = Publishing.objects.filter(listing__product=product).exists() or \
            Publishing.objects.filter(listing__product__in=[pset.composite for pset in ps]).exists()
        if has_publishings:
            return HttpResponseForbidden()

        # delete all associated listings
        product.listings.all().delete()
        for product_set in ps:
            product_set.composite.listings.all().delete()

        return super(ProductDeleteView, self).delete(request, *args, **kwargs)


class ProductUpdateView(LoginRequiredMixin, BazaarPrefixMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy("bazaar:product-detail", kwargs={'pk': self.object.id})


# class CompositeProductCreateView(LoginRequiredMixin, BazaarPrefixMixin, generic.CreateView):
#     model = CompositeProduct
#     form_class = CompositeProductForm
#
#     fields = ['name', 'description', 'photo', 'price']
#     template_name = "goods/compositeproduct_form.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(CompositeProductCreateView, self).get_context_data(**kwargs)
#         context['formset'] = ProductSetFormSet()
#         return context
#
#     def get_success_url(self):
#         return reverse_lazy("bazaar:product-detail", kwargs={'pk': self.object.id})


def CompositeProductView(request):
    if request.method == 'POST':
        form = CompositeProductForm(request.POST)
        formset = ProductSetFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            new_composite = form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                instance.composite = new_composite
                instance.save()
            formset.save_m2m()
    else:
        form = CompositeProductForm()
        formset = ProductSetFormSet(queryset=ProductSet.objects.none())
    return render_to_response('bazaar/goods/compositeproduct_form.html',
                              {'form': form, 'formset': formset},
                              context_instance=RequestContext(request))
