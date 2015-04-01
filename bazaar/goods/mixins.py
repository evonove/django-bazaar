from __future__ import absolute_import
from __future__ import unicode_literals

from django.db import transaction

from ..warehouse import api


class MovableMixin(object):
    def move(self, from_location, to_location, quantity=1, price_multiplier=1, **kwargs):
        """
        Here there will be the implementation of tha strategy used to move the product from one location to another
        :param from_location:
        :param to_location:
        :param kwargs:
        """
        pass


class MovableProductMixin(MovableMixin):

    @transaction.atomic
    def move(self, from_location, to_location, quantity=1, price_multiplier=1, **kwargs):
        """
        With simple products we just call the warehouse api to move the product
        from a location to another, with the possibility to specify quantity,
        a price_multiplier (of the product's price), the agent who moved the product and additional notes.
        """
        price = self.price * price_multiplier
        agent = kwargs.get('agent', 'bazaar')
        note = kwargs.get('note', '')
        api.move(from_location, to_location, self, quantity, price, agent=agent, note=note)
        # FIXME: unit price should be unit_cost
        unit_price = 0

        for ps in self.sets.all():
            quantities = []
            composite = ps.composite
            for cps in composite.product_sets.all():
                quantity = api.get_storage_quantity(cps.product)
                product_price = api.get_storage_price(cps.product)
                quantities.append(quantity // cps.quantity)
                unit_price = unit_price + (product_price.amount * cps.quantity)
            from ..warehouse.models import Stock

            stock_outgoing, created = Stock.objects.get_or_create(product=composite, location=to_location)
            stock_incoming, created = Stock.objects.get_or_create(product=composite, location=from_location)

            movement_quantity = abs(stock_incoming.quantity - min(quantities))

            stock_incoming.quantity -= movement_quantity
            stock_incoming.save()

            stock_outgoing.unit_price = unit_price
            stock_outgoing.quantity += movement_quantity
            stock_outgoing.save()


class MovableCompositeProductMixin(MovableMixin):

    @transaction.atomic
    def move(self, from_location, to_location, quantity=1, price_multiplier=1, **kwargs):
        """
        Here we implement the strategy for products composed by more products in different quantities.
        Here we assume that composite products' availability is given by the number of single products
        in the stock, so we don't permit to add composite products in the storage, and they can only go from storage
        locations to output locations.
        """
        from ..warehouse.models import Location
        LOCATION_PIPELINE = {
            Location.LOCATION_STORAGE: (Location.LOCATION_CUSTOMER, Location.LOCATION_OUTPUT),
            Location.LOCATION_OUTPUT: (Location.LOCATION_CUSTOMER, Location.LOCATION_STORAGE),
        }

        price = self.price * price_multiplier
        agent = kwargs.get('agent', 'composite')
        note = kwargs.get('note', '')

        if to_location.type in LOCATION_PIPELINE.get(from_location.type):

            # If the composite is going out of the storage, we actually move it
            api.move(from_location, to_location, self, quantity, price, agent=agent, note=note)

            for product_set in self.compositeproduct.product_sets.all():
                product = product_set.product
                product_quantity = product_set.quantity * quantity
                product.move(from_location, to_location, quantity=product_quantity,
                             price_multiplier=price_multiplier, **kwargs)
