from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import IntegerField, CharField
from bazaar.helpers import FormHelperMixin


class ListingForm(FormHelperMixin, forms.Form):
    title = CharField()
    description = CharField(required=False)
    picture_url = CharField(required=False)
    product = CharField()
    quantity = IntegerField()

    def get_form_helper(self):
        helper = FormHelper(self)
        helper.layout.append(Submit("save", "save"))
        return helper