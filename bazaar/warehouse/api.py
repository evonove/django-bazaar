from __future__ import unicode_literals

from django.db import DatabaseError

from .exceptions import MovementException
from .models import Movement
from .signals import incoming_movement, outgoing_movement


def move(from_location, to_location, product, quantity, unit_price, agent=None, note=None):
    """Move a product from `from_location` to `to_location`"""
    agent = agent or ""
    note = note or ""

    if quantity < 0:
        raise MovementException("Quantity must be a positive amount")

    try:
        movement = Movement.objects.create(
            from_location=from_location, to_location=to_location, product=product,
            quantity=quantity, unit_price=unit_price, agent=agent, note=note
        )
    except DatabaseError as de:
        raise MovementException(de)

    incoming_movement.send(sender=to_location, movement=movement)
    outgoing_movement.send(sender=from_location, movement=movement)
