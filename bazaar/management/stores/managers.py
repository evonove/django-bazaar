from __future__ import unicode_literals

from django_filters import FilterSet


class DefaultStoreManager(object):
    """
    Mandatory overrides: get_store_name, get_publishing_template
    """
    extras = {}

    def get_store_name(self):
        raise NotImplementedError("You need to provide a store name!")

    def get_store_description(self):
        return ""

    def get_store_url(self):
        return ""

    def get_store_actions(self):
        return []

    def get_store_filter(self):
        return FilterSet()

    def get_store_forms(self):
        return []

    def get_store_publishing_template(self):
        #TODO create a default publishing template
        raise NotImplementedError("You need to publishing template!")

    def get_store_extra(self, extra_name):
        return self.extras[extra_name]