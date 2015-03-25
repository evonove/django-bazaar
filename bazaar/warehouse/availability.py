from __future__ import unicode_literals

from ..listings.models import Order


class BaseAvailabilityBackend(object):
    def available(self, *args, **kwargs):
        raise NotImplementedError


class AvailabilityBackend(object):
    # TODO: TEST THIS ONE
    def available(self, stock):
        pending = Order.objects.filter(
            publishing__listing__product=stock.product
        ).filter(status=Order.ORDER_PENDING).extra(
            select={"pending": "SUM(COALESCE(products.quantity, 1) * listings_order.quantity)"}
        ).values("pending")[0]["pending"]

        return stock.quantity - (pending or 0)
