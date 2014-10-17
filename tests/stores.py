from __future__ import absolute_import
from __future__ import unicode_literals

from bazaar.listings.stores.strategies import DefaultStoreStrategy


class Store1(DefaultStoreStrategy):
    def get_store_name(self):
        return "Store 1"


class Store2(DefaultStoreStrategy):
    def get_store_name(self):
        return "Store 2"
