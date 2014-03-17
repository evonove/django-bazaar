from __future__ import unicode_literals

from bazaar.utils import money_to_default, has_default_currency

from .exceptions import MovementException
from .models import Movement
from .signals import incoming_movement, outgoing_movement


def move(from_location, to_location, product, quantity, unit_price, agent=None, note=None):
    """Move a product from `from_location` to `to_location`"""
    agent = agent or ""
    note = note or ""

    # convert price to default currency (whether different)
    # and save the original in original_unit_price
    if not has_default_currency(unit_price):
        original_unit_price = unit_price
        unit_price = money_to_default(unit_price)
    else:
        original_unit_price = None

    if quantity < 0:
        raise MovementException("Quantity must be a positive amount")

    try:
        movement = Movement.objects.create(
            from_location=from_location, to_location=to_location, product=product,
            quantity=quantity, unit_price=unit_price, original_unit_price=original_unit_price,
            agent=agent, note=note
        )
    except Exception as de:
        raise MovementException(de)

    incoming_movement.send(sender=to_location, movement=movement)
    outgoing_movement.send(sender=from_location, movement=movement)
