from __future__ import unicode_literals
from django.core.urlresolvers import reverse_lazy

from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, ButtonHolder, HTML, Layout
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
    def disable_save(self):
        return False

    def disable_delete(self):
        return False

    def get_form_helper(self):
        attrs = (
            'form',
            'form_class',
            'layout',
            'form_tag',
            'form_error_title',
            'formset_error_title',
            'form_show_errors',
            'render_unmentioned_fields',
            'render_hidden_fields',
            'render_required_fields',

            'html5_required',
            'form_show_labels',
            'template',
            'field_template',
            'disable_csrf',
            'label_class',
            'label_size',
            'field_class',)

        metahelper_dict = self.MetaHelper.__dict__
        for name in list(set(metahelper_dict.keys()) & set(attrs)):
            if hasattr(FormHelper, name):
                setattr(FormHelper, name, metahelper_dict[name])

        helper = FormHelper(self)
        helper.form_class = "form-horizontal"
        helper.label_class = "col-md-3"
        helper.field_class = "col-md-8"

        extended_fields = self.MetaHelper.extended_fields if hasattr(self.MetaHelper, 'extended_fields') else []
        list_url = reverse_lazy(self.MetaHelper.name_list_url, kwargs={}) if self.MetaHelper.name_list_url else '#'

        is_modelform = hasattr(self, 'instance')
        has_instance = is_modelform and hasattr(self.instance, 'pk') and self.instance.pk is not None

        submit_disabled = 'disabled="disabled"' if is_modelform and self.disable_save() else ''
        delete_disabled = 'disabled="disabled"' if is_modelform and (self.disable_delete() or not has_instance) else ''

        has_back_button = getattr(self.MetaHelper, 'has_back_button',
                                  FormModelHelperMixin.MetaHelper.has_back_button)
        has_button_toolbar = getattr(self.MetaHelper, 'has_button_toolbar',
                                     FormModelHelperMixin.MetaHelper.has_button_toolbar)

        save_html = '<input type="submit" name="save" value="{}" class="btn btn-primary" ' \
                    'id="submit-id-save" {}>'.format(_("submit").title(), submit_disabled)
        delete_html = '&nbsp;<a data-toggle="modal" href="#modalDelete" class="btn btn-danger pull-right" {}>' \
                      '<i class="glyphicon glyphicon-trash"></i>&nbsp;{}' \
                      '</a>'.format(delete_disabled, _('Delete'.title()), ) if is_modelform else ''
        back_html = '<a href="{}" class="btn btn-default" data-dismiss="modal">' \
                    '<i class="glyphicon glyphicon-chevron-left"></i>&nbsp;{}' \
                    '</a>&nbsp;'.format(list_url, _('back'.title())) if has_back_button else ''

        if extended_fields:
            helper.layout = Layout(
                TabHolder(
                    Tab(_('general attributes').title(),
                        *self.fields.keys()),
                    Tab(_('specific attributes').title(),
                        extended_fields)
                )
            )
        if has_button_toolbar:
            helper.layout.append(
                Div(
                    Div(
                        ButtonHolder(
                            HTML(back_html),
                            HTML(save_html),
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
        has_back_button = True
        has_button_toolbar = True


class FormHelperMixinNoTag(FormHelperMixin):
    def get_form_helper(self):
        helper = super(FormHelperMixinNoTag, self).get_form_helper()
        helper.form_tag = False

        return helper
