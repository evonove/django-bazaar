"""
This module aims to handle denormalized stock data handling proper
signals from models.
"""

from __future__ import division
from __future__ import unicode_literals

import logging

from django.dispatch import receiver

from .models import Stock, Location
from .signals import incoming_movement, outgoing_movement, lost_and_found_changed, supplier_changed, storage_changed, output_changed, customer_changed


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
    _changed_location_signal_sender(stock)


@receiver(outgoing_movement)
def update_stock_on_outgoing(sender, movement, **kwargs):
    stock, created = Stock.objects.get_or_create(location=sender, product=movement.product)

    stock.quantity = stock.quantity - movement.quantity
    stock.save()
    _changed_location_signal_sender(stock)


def _changed_location_signal_sender(stock):
    if stock.location.type == Location.LOCATION_LOST_AND_FOUND:
        lost_and_found_changed.send(sender=stock, product=stock.product)
    elif stock.location.type == Location.LOCATION_SUPPLIER:
        supplier_changed.send(sender=stock, product=stock.product)
    elif stock.location.type == Location.LOCATION_STORAGE:
        storage_changed.send(sender=stock, product=stock.product)
    elif stock.location.type == Location.LOCATION_OUTPUT:
        output_changed.send(sender=stock, product=stock.product)
    elif stock.location.type == Location.LOCATION_CUSTOMER:
        customer_changed.send(sender=stock, product=stock.product)