from __future__ import unicode_literals

from ...settings import bazaar_settings


class ListingsLoader(object):

    def __init__(self):
        self.listing_filter = bazaar_settings.LISTING_FILTER

    def get_listing_filter(self):
        return self.listing_filter


listings_loader = ListingsLoader()