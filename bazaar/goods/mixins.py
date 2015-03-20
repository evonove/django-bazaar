from __future__ import absolute_import
from __future__ import unicode_literals
from bazaar.warehouse import api


class MoveableProductMixin(object):

    def move(self, from_location, to_location, **kwargs):
        quantity = kwargs.pop('quantity', 1)
        price_multiplier = kwargs.pop('price_multiplier', 1)
        if not hasattr(self, 'compositeproduct'):
            price = self.price * price_multiplier
            agent = kwargs.get('agent', 'merchant')
            note = kwargs.get('note', '')
            api.move(
                from_location,
                to_location,
                self,
                quantity,
                price,
                agent=agent,
                note=note
            )
        else:
            for product_set in self.compositeproduct.product_sets.all():
                product = product_set.product
                product_quantity = product_set.quantity * quantity
                product.move(from_location, to_location, quantity=product_quantity, price_multiplier=price_multiplier,
                             **kwargs)
