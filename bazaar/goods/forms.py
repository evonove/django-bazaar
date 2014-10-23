from __future__ import absolute_import
from __future__ import unicode_literals
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div

from django import forms
from django.core.exceptions import ValidationError
from bazaar.goods.models import Product
from bazaar.helpers import FormHelperMixin


def ean_uniqueness(ean):
    if Product.objects.filter(ean=ean).exists():
        raise ValidationError(u'A product with this ean already exists')


class ProductForm(FormHelperMixin, forms.ModelForm):
    ean = forms.CharField(max_length=20, required=False, validators=[ean_uniqueness])

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
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
                    HTML("""<a class="btn btn-default" href="{% url 'bazaar:product-list' %}">"""
                         """<i class="glyphicon glyphicon-chevron-left"></i>&nbsp;Back</a>&nbsp;"""),
                    Submit('save', 'Submit'),
                    css_class="col-md-8 col-md-offset-3"
                ),
                css_class="form-group"
            )
        )

    class Meta:
        model = Product
        exclude = ("price_lists", )
