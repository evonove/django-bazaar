from __future__ import unicode_literals

from django import forms

from ..helpers import FormHelperMixinNoTag
from .models import Movement


class MovementForm(FormHelperMixinNoTag, forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['product', 'from_location', 'to_location', 'unit_price', 'quantity', 'note']

    def __init__(self, *args, **kwargs):
        super(MovementForm, self).__init__(*args, **kwargs)

        # hide product field when a value is provided in initial dict
        if "product" in kwargs["initial"]:
            self.fields["product"].widget = forms.HiddenInput()
