from django.views import generic

from braces.views import LoginRequiredMixin

from ..mixins import BazaarPrefixMixin
from .models import Product


class ProductListView(LoginRequiredMixin, BazaarPrefixMixin, generic.ListView):
    model = Product
    paginate_by = 20


class ProductCreateView(LoginRequiredMixin, BazaarPrefixMixin, generic.CreateView):
    model = Product
