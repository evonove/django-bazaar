from __future__ import unicode_literals

from ..compat import atomic
from .exceptions import MovementException
from .models import Movement, Stock


@atomic
def in_movement(quantity, agent, reason, product, price=None):
    """ Create a incoming movement for the `product` """
    if quantity < 0:
        raise MovementException("Quantity must be a positive amount")

    # otherwise create a stock
    stock, created = Stock.objects.get_or_create(product=product)

    # when price is None is defaulted to the current stock price, which by default is the average
    if price is None:
        price = stock.price

    Movement.objects.create(quantity=quantity, agent=agent, reason=reason, stock=stock, price=price)


@atomic
def out_movement(quantity, agent, reason, product):
    """ Create an output movement for the given `product`. """

    if quantity < 0:
        raise MovementException("Quantity must be a positive amount")

    try:
        stock = Stock.objects.get(product=product)
        Movement.objects.create(quantity=quantity * -1, agent=agent, reason=reason, stock=stock)
    except Stock.DoesNotExist:
        raise MovementException("No stock found for product '%s'" % product)
