from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.bootstrap import StrictButton


class FormHelperMixin(object):
    """
    TODO: add a comment
    """
    @property
    def helper(self):
        if not hasattr(self, "_helper"):
            helper = FormHelper(self)
            helper.form_class = "form-horizontal"
            helper.label_class = "col-md-2"
            helper.field_class = "col-md-10"
            helper.form_tag = False

            helper.layout.append(
                Div(
                    Div(
                        StrictButton(_("Submit"), css_class="btn-primary", type="submit"),
                        css_class="col-md-offset-2 col-md-10",
                    ),
                    css_class="form-group"
                ),
            )

            self._helper = helper

        return self._helper
