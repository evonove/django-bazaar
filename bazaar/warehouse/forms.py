from __future__ import unicode_literals

from decimal import Decimal

from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext as _

from bazaar.settings import bazaar_settings

from djmoney.forms.fields import MoneyField

from ..goods.models import Product
from ..helpers import FormHelperMixin


class BaseMovementForm(FormHelperMixin, forms.Form):
    product = forms.IntegerField()
    quantity = forms.DecimalField(validators=[MinValueValidator(Decimal('0.01'))])
    notes = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(BaseMovementForm, self).__init__(*args, **kwargs)

        # hide product field when a value is provided in initial dict
        if "product" in kwargs["initial"]:
            self.fields["product"].widget = forms.HiddenInput()

    def clean_product(self):
        data = self.cleaned_data["product"]
        try:
            product = Product.objects.get(pk=data)
        except Product.DoesNotExist:
            raise forms.ValidationError(_("Product with id %s does not exist" % data))

        return product


class MovementOutForm(BaseMovementForm):
    pass


class MovementInForm(BaseMovementForm):
    price = MoneyField(currency_choices=bazaar_settings.CURRENCIES)

    def __init__(self, *args, **kwargs):
        super(MovementInForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ["product", "quantity", "price", "notes"]
