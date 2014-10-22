from __future__ import absolute_import
from __future__ import unicode_literals
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Button, Layout, Fieldset, ButtonHolder, Submit, HTML, Div

from django import forms
from bazaar.goods.models import Product
from bazaar.helpers import FormHelperMixin


class ProductForm(FormHelperMixin, forms.ModelForm):
    ean = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        super(FormHelperMixin, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                '',
                'name',
                'description',
                'ean',
                'photo',
                'price'
            ),
            FormActions(
                Div(
                    Submit('save', 'Submit'),
                    HTML("""<a class="btn btn-default" href="{% url 'bazaar:product-list' %}">Cancel</a>"""),

                    css_class="col-md-8 col-md-offset-3"
                ),
                css_class="form-group"
            )
        )
        # self.helper.add_input(FormActions(Button('cancel', 'Cancel')))

    class Meta:
        model = Product
        # exclude = ("price_lists", )
