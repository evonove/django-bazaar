from __future__ import unicode_literals

import django.dispatch


product_price_changed = django.dispatch.Signal(providing_args=["product"])
product_stock_changed = django.dispatch.Signal(providing_args=["quantity"])
