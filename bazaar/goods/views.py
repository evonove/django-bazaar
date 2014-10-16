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


class ProductUpdateView(LoginRequiredMixin, BazaarPrefixMixin, generic.UpdateView):
    model = Product
    fields = ['name']
    success_url = '/products'

    # TODO: To be finished
    def form_valid(self, form):
        name = form.cleaned_data["name"]
        product = self.object
        product.name = name
        product.save()
        return super(ProductUpdateView, self).form_valid(form)

class ProductDeleteView(LoginRequiredMixin, BazaarPrefixMixin, generic.DeleteView):
    model = Product
