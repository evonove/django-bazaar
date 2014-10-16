from __future__ import absolute_import
from __future__ import unicode_literals


from django.apps import AppConfig


class ListingsConfig(AppConfig):
    name = "bazaar.listings"
    verbose_name = "Bazaar Listings"

    def ready(self):
        # import signals module to attach handlers to signals
        from . import signals  # noqa
