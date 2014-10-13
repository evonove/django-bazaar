from __future__ import absolute_import
from __future__ import unicode_literals


from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    name = "bazaar.warehouse"
    verbose_name = "Bazaar Warehouse"

    def ready(self):
        # import stock module to attach handlers to signals
        from . import stocks  # noqa
