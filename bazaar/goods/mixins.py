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

        for ps in self.sets.all():
            to_location_quantities = []
            from_location_quantities = []

            to_location_unit_cost = 0
            from_location_unit_cost = 0

            composite = ps.composite

            for cps in composite.product_sets.all():
                to_location_product_quantity = api.get_stock_quantity(cps.product, location_type=to_location.type)
                to_location_product_price = api.get_stock_price(cps.product, location_type=to_location.type)
                to_location_quantities.append(to_location_product_quantity // cps.quantity)
                to_location_unit_cost += (to_location_product_price.amount * cps.quantity)

                from_location_product_quantity = api.get_stock_quantity(cps.product, location_type=from_location.type)
                from_location_product_price = api.get_stock_price(cps.product, location_type=from_location.type)
                from_location_quantities.append(from_location_product_quantity // cps.quantity)
                from_location_unit_cost += (from_location_product_price.amount * cps.quantity)
            from ..warehouse.models import Stock

            stock_outgoing, created = Stock.objects.get_or_create(product=composite, location=to_location)
            stock_incoming, created = Stock.objects.get_or_create(product=composite, location=from_location)

            stock_incoming.unit_price = from_location_unit_cost
            stock_outgoing.unit_price = to_location_unit_cost
            # Update from_location quantity and price

            new_incoming_quantity = min(from_location_quantities)
            stock_incoming.quantity = 0 if new_incoming_quantity < 0 else new_incoming_quantity
            stock_incoming.save()

            # Update to_location quantity and price

            new_outgoing_quantity = min(to_location_quantities)
            stock_outgoing.quantity = 0 if new_outgoing_quantity < 0 else new_outgoing_quantity
            stock_outgoing.save()

            from bazaar.warehouse.stocks import _send_changed_location
            _send_changed_location(stock_incoming)
            _send_changed_location(stock_outgoing)


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
        location_pipeline = {
            Location.LOCATION_STORAGE: (Location.LOCATION_CUSTOMER, Location.LOCATION_OUTPUT),
            Location.LOCATION_OUTPUT: (Location.LOCATION_CUSTOMER, Location.LOCATION_STORAGE),
        }

        allowed_locations = location_pipeline.get(from_location.type)

        if allowed_locations and to_location.type in allowed_locations:

            for product_set in self.compositeproduct.product_sets.all():
                product = product_set.product
                product_quantity = product_set.quantity * quantity
                product.move(from_location, to_location, quantity=product_quantity,
                             price_multiplier=price_multiplier, **kwargs)
