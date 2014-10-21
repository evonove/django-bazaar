from __future__ import absolute_import
from __future__ import unicode_literals

from django import forms
from bazaar.goods.models import Product
from bazaar.helpers import FormHelperMixin


class ProductForm(FormHelperMixin, forms.ModelForm):
    ean = forms.CharField(max_length=20, required=False)

    class Meta:
        model = Product
        exclude = ("price_lists", )

