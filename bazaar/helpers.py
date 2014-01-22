from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.bootstrap import StrictButton


class FormHelperMixin(object):
    """
    TODO: add a comment
    """
    def get_form_helper(self):
        helper = FormHelper(self)
        helper.form_class = "form-horizontal"
        helper.label_class = "col-md-3"
        helper.field_class = "col-md-8"

        helper.layout.append(
            Div(
                Div(
                    StrictButton(_("Submit"), css_class="btn-primary", type="submit"),
                    css_class="col-md-offset-3 col-md-8",
                ),
                css_class="form-group"
            ),
        )
        return helper

    @property
    def helper(self):
        if not hasattr(self, "_helper"):
            self._helper = self.get_form_helper()

        return self._helper


class FormHelperMixinNoTag(FormHelperMixin):
    def get_form_helper(self):
        helper = super(FormHelperMixinNoTag, self).get_form_helper()
        helper.form_tag = False

        return helper
