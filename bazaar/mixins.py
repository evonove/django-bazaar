from __future__ import unicode_literals


class TemplateNamePrefixMixin(object):
    """
    This mixin prepend `template_prefix` to template names
    """
    template_prefix = None

    def get_template_names(self):
        names = super(TemplateNamePrefixMixin, self).get_template_names()

        if self.template_prefix:
            return ["%s/%s" % (self.template_prefix, name) for name in names]
        else:
            return names


class BazaarPrefixMixin(TemplateNamePrefixMixin):
    template_prefix = "bazaar"
