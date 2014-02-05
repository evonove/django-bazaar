from __future__ import unicode_literals

from ..listings.models import Order


class BaseAvailabilityBackend(object):
    def available(self, *args, **kwargs):
        raise NotImplementedError


class AvailabilityBackend(object):
    def available(self, stock):
        pending = Order.objects.filter(
            publishing__listing__listing_sets__product=stock.product
        ).filter(status=Order.ORDER_PENDING).extra(
            select={"pending": "SUM(listings_listingset.quantity * listings_order.quantity)"}
        ).values("pending")[0]["pending"]

        return stock.quantity - (pending or 0)
