from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import IntegerField, CharField, Textarea
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from bazaar.goods.models import Product
from ..helpers import FormHelperMixin
from .models import Publishing


class ListingForm(FormHelperMixin, forms.Form):
    title = CharField()
    description = CharField(required=False, widget=Textarea)
    picture_url = CharField(required=False)
    product = IntegerField()
    quantity = IntegerField()

    def get_form_helper(self):
        helper = FormHelper(self)
        helper.layout.append(Submit("save", "save"))
        return helper

    def get_product(self):
        product_id = self.cleaned_data.get("product")
        return Product.objects.get(id=int(product_id))

    def product_exists(self):
        product_id = self.cleaned_data.get("product")
        return Product.objects.filter(id=int(product_id)).exists()

    def is_valid(self):
        """
        Returns True if the form has no errors. Otherwise, False. If errors are
        being ignored, returns False.
        """
        form_is_valid = super(ListingForm, self).is_valid()
        if form_is_valid:
            try:
                self.product_exists()
            except Product.DoesNotExist:
                errors = self._errors.setdefault(forms.NON_FIELD_ERRORS, ErrorList())
                errors.append(_("Update is denied. Product does not exist."))
                form_is_valid = False
            except ValueError:
                errors = self._errors.setdefault(forms.NON_FIELD_ERRORS, ErrorList())
                errors.append(_("Update is denied. Product id is invalid."))
                form_is_valid = False

        return form_is_valid


class PublishingForm(forms.ModelForm):

    class Meta:
        model = Publishing
