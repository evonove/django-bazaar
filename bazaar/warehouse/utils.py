from __future__ import unicode_literals

from .models import Movement, Stock


def create_movement(quantity, agent, reason, stock=None, code=None, product=None, price=None):
    # when stock is empty try to get or create one
    if not stock:

        # if code is specified try to get the stock with that code or create one
        if code:
            stock, created = Stock.objects.get_or_create(
                code=code, defaults={"product": product, "price": price})
        else:
            # otherwise create a stock
            stock = Stock.objects.create(product=product, price=price)

    # TODO: emit a custom signal when movement is created (or use post_save??)
    return Movement.objects.create(quantity=quantity, agent=agent, reason=reason, stock=stock)
