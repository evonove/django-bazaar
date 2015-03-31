from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import IntegerField, CharField, Textarea
from django.utils.translation import ugettext as _
from bazaar.goods.models import Product
from ..helpers import FormHelperMixin
from .models import Publishing


class ListingForm(FormHelperMixin, forms.Form):
    product = IntegerField()

    def get_form_helper(self):
        helper = FormHelper(self)
        helper.layout.append(Submit("save", "save"))
        return helper

    def clean_product(self):
        product_id = self.cleaned_data.get("product")
        try:
            Product.objects.get(id=product_id)
            return product_id
        except Product.DoesNotExist:
            self.add_error("product", _("Update is denied. Product does not exist."))
        except ValueError:
            self.add_error("product", _("Update is denied. Product id is invalid."))


class PublishingForm(forms.ModelForm):

    class Meta:
        model = Publishing
