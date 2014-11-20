from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import IntegerField, CharField, Textarea
from django.forms.widgets import TextInput
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


class PublishingForm(forms.ModelForm):

    class Meta:
        model = Publishing
