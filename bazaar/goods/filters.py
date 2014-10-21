from __future__ import absolute_import
from __future__ import unicode_literals
import django_filters
from bazaar.filters import BaseFilterSet
from bazaar.goods.models import Product


class ProductFilter(BaseFilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Product
        exclude = ('price', 'price_lists', 'price_currency')
