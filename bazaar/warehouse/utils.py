from __future__ import unicode_literals

from django.db.models import Sum

from ..compat import atomic
from .exceptions import MovementException
from .models import Movement, Stock


@atomic
def in_movement(quantity, agent, reason, price, product, code=None):
    """ Create a incoming movement for the `product` """
    if quantity < 0:
        raise MovementException("Quantity must be a positive amount")

    # if code is specified try to get the stock with that code or create one
    if code:
        stock, created = Stock.objects.get_or_create(
            code=code, defaults={"product": product, "price": price})
    else:
        # otherwise create a stock
        stock = Stock.objects.create(product=product, price=price)

    # TODO: emit a custom signal when movement is created (or use post_save??)
    Movement.objects.create(quantity=quantity, agent=agent, reason=reason, stock=stock)


@atomic
def out_movement(quantity, agent, reason, product=None, code=None):
    """ Create an output movement for the given `product`. """

    if quantity < 0:
        raise MovementException("Quantity must be a positive amount")

    if not (product or code):
        raise MovementException("Movement out need at least a product or a code")

    if code:
        try:
            stock = Stock.objects.get(code=code)
            # TODO: emit a custom signal when movement is created (or use post_save??)
            Movement.objects.create(quantity=quantity * -1, agent=agent, reason=reason, stock=stock)
        except Stock.DoesNotExist:
            raise MovementException("Stock with code %s do not exists" % code)
    else:
        stocks = Stock.objects.filter(product=product, code="")

        if stocks.count() == 0:
            raise MovementException("No stocks found for product '%s'" % product)

        for stock in stocks.annotate(qta=Sum("movements__quantity")):
            if stock.qta <= 0:
                continue

            if stock.qta < quantity:
                q = stock.qta
            else:
                q = quantity

            Movement.objects.create(quantity=q * -1, agent=agent, reason=reason, stock=stock)
            quantity -= q

            if quantity == 0:
                break

        if quantity > 0:
            stock = stocks.latest()
            # TODO: emit a custom signal when movement is created (or use post_save??)
            Movement.objects.create(quantity=quantity * -1, agent=agent, reason=reason, stock=stock)
