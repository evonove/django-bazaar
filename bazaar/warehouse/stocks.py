"""
This module aims to handle denormalized stock data handling proper
signals from models.
"""

from __future__ import division
from __future__ import unicode_literals

import logging

from django.dispatch import receiver

from .models import Stock
from .signals import incoming_movement, outgoing_movement


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


@receiver(outgoing_movement)
def update_stock_on_outgoing(sender, movement, **kwargs):
    stock, created = Stock.objects.get_or_create(location=sender, product=movement.product)

    stock.quantity = stock.quantity - movement.quantity
    stock.save()
