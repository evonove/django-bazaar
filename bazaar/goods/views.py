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


class ProductDeleteView(LoginRequiredMixin, BazaarPrefixMixin, generic.DeleteView):
    model = Product

