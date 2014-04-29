"""
This module aims to handle denormalized stock data handling proper
signals from models.
"""

from __future__ import division
from __future__ import unicode_literals

import logging
import warnings

from django.dispatch import receiver

from .models import Stock, Location
from .signals import (incoming_movement, outgoing_movement, lost_and_found_changed, unknown_changed,
                      supplier_changed, storage_changed, output_changed, customer_changed)


logger = logging.getLogger(__name__)


@receiver(incoming_movement)
def update_stock_on_incoming(sender, movement, **kwargs):
    stock, created = Stock.objects.get_or_create(location=sender, product=movement.product)

    # new stock quantity
    quantity = stock.quantity + movement.quantity

    # update average unit price
    divider = quantity if quantity else 2

    avg_unit_price = (stock.value + movement.value) / divider

    stock.quantity = quantity
    stock.unit_price = avg_unit_price
    stock.save()

    _send_changed_location(stock)


@receiver(outgoing_movement)
def update_stock_on_outgoing(sender, movement, **kwargs):
    stock, created = Stock.objects.get_or_create(location=sender, product=movement.product)

    stock.quantity = stock.quantity - movement.quantity
    stock.save()

    _send_changed_location(stock)


def _send_changed_location(stock):
    if stock.location.type == Location.LOCATION_LOST_AND_FOUND:
        signal = lost_and_found_changed
    elif stock.location.type == Location.LOCATION_SUPPLIER:
        signal = supplier_changed
    elif stock.location.type == Location.LOCATION_STORAGE:
        signal = storage_changed
    elif stock.location.type == Location.LOCATION_OUTPUT:
        signal = output_changed
    elif stock.location.type == Location.LOCATION_CUSTOMER:
        signal = customer_changed
    else:
        warnings.warn("Unknown location type '%s' has changed" % stock.location.type)
        signal = unknown_changed

    signal.send(sender=stock, product=stock.product)
