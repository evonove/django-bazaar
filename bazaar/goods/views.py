from django.views import generic

from ..mixins import BazaarPrefixMixin
from .models import Product


class ProductListView(BazaarPrefixMixin, generic.ListView):
    model = Product
    paginate_by = 20


class ProductCreateView(BazaarPrefixMixin, generic.CreateView):
    model = Product
