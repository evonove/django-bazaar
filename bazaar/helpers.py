from __future__ import unicode_literals
from django.core.urlresolvers import reverse_lazy

from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, ButtonHolder, HTML, Submit, Layout
from crispy_forms.bootstrap import TabHolder, Tab, StrictButton


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


class FormModelHelperMixin(FormHelperMixin):

    def get_form_helper(self):
        helper = FormHelper(self)
        helper.form_class = "form-horizontal"
        helper.label_class = "col-md-3"
        helper.field_class = "col-md-8"

        extended_fields = self.MetaHelper.extended_fields if hasattr(self.MetaHelper, 'extended_fields') else []
        list_url = reverse_lazy(self.MetaHelper.name_list_url, kwargs={}) if self.MetaHelper.name_list_url else '#'

        is_modelform = hasattr(self, 'instance')
        has_instance = is_modelform and hasattr(self.instance, 'pk') and self.instance.pk is not None
        disabled = 'disabled="disabled"' if is_modelform and not has_instance else ''
        from bazaar.listings.stores import stores_loader
        if is_modelform and hasattr(self.instance, 'store') and \
                not stores_loader.get_store_strategy(self.instance.store.slug).get_publishing_delete_action():
            disabled = 'disabled="disabled"'
        delete_html = '&nbsp;<a data-toggle="modal" href="#modalDelete" class="btn btn-danger pull-right" {}>' \
                      '<i class="glyphicon glyphicon-trash"></i>&nbsp;{}' \
                      '</a>'.format(disabled, _('Delete'.title()), ) if is_modelform else ''

        if extended_fields:
            helper.layout = Layout(
                TabHolder(
                    Tab(_('general attributes').title(),
                        *self.fields.keys()),
                    Tab(_('specific attributes').title(),
                        extended_fields)
                )
            )

        helper.layout.append(
            Div(
                Div(
                    ButtonHolder(
                        HTML('<a '
                             'href="{}" '
                             'class="btn btn-default" data-dismiss="modal">'
                             '<i class="glyphicon glyphicon-chevron-left"></i>&nbsp;{}'
                             '</a>&nbsp;'.format(list_url, _('back'.title()))),
                        Submit('save', _("Submit")),
                        HTML(delete_html)
                    ),
                    css_class="col-md-offset-3 col-md-8",
                ),
                css_class="form-group"
            ),
        )
        return helper

    class MetaHelper:
        """
        Accepted attrs:
        name_url_list: url name to back to list view.
        name_delete_url: url name to back delete object.
        readonly_fields: set some model fields as read_only.
        extended_fields: set model fields layout in two tabs. Extended_fields will go in the second tab.
        readonly_fields_if_not_empty: set some model fields as read_only only after are set, as listing in publishing
        """
        name_list_url = None
        name_delete_url = None
        readonly_fields = []
        extended_fields = []
        readonly_fields_if_not_empty = []


class FormHelperMixinNoTag(FormHelperMixin):
    def get_form_helper(self):
        helper = super(FormHelperMixinNoTag, self).get_form_helper()
        helper.form_tag = False

        return helper
