from __future__ import unicode_literals
from ..models import Publishing

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

    def get_publishing_create_url(self):
        return None

    def get_model(self):
        return Publishing

    def get_publishing_form(self):
        return None

    def get_publishing_delete_action(self):
        return None

    def get_publishing_update_action(self):
        return None

    def get_publishing_create_action(self):
        return None

    def get_store_publishing_template(self):
        raise NotImplementedError("You need to listing-list publishing template!")

    def get_store_publishing_list_template(self):
        raise NotImplementedError("You need to provide publishing-list template!")

    def get_store_extra(self, extra_name):
        return self.extras[extra_name]

    def get_publishing_discounted_price(self, price):
        return price
