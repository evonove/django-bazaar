from __future__ import absolute_import
from __future__ import unicode_literals

from bazaar.listings.stores.managers import DefaultStoreManager


class Store1(DefaultStoreManager):
    def get_store_name(self):
        return "Store 1"


class Store2(DefaultStoreManager):
    def get_store_name(self):
        return "Store 2"
