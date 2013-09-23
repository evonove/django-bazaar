from django.db import models
from django.views import generic

from .models import Product


class ProductListView(generic.ListView):
    model = Product
    template_name = "bazaar/goods/product_list.html"


class ProductCreateView(generic.CreateView):
    model = Product
    template_name = "bazaar/goods/product_form.html"