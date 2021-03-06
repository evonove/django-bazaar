from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from bazaar.goods.models import Product

from .models import Order, Publishing, Listing


class OrderProcessor(object):
    order_model = Order
    publishing_model = Publishing

    order_lookup_id = None
    publishing_lookup_id = None

    def __init__(self):
        self._messages = []

    def get_order_model(self):
        if self.order_model is None:
            raise ImproperlyConfigured("OrderProcessor requires 'order_model' to be defined")

        return self.order_model

    def get_publishing_model(self):
        if self.publishing_model is None:
            raise ImproperlyConfigured("OrderProcessor requires 'publishing_model' to be defined")

        return self.publishing_model

    def get_order_lookup_id(self):
        if self.order_lookup_id is None:
            raise ImproperlyConfigured("OrderProcessor requires 'order_lookup_id' to be defined")

        return self.order_lookup_id

    def get_publishing_lookup_id(self):
        if self.publishing_lookup_id is None:
            raise ImproperlyConfigured("OrderProcessor requires 'publishing_lookup_id' to be defined")

        return self.publishing_lookup_id

    def _get_product_subclass(self, product, id):
        return product.__class__.objects.get_subclass(id=id)

    def get_order(self, incoming):
        external_id = getattr(incoming, self.get_order_lookup_id())
        model = self.get_order_model()
        try:
            order = model.objects.get(external_id=external_id)
            if order.publishing is not None and order.publishing.listing is not None \
                    and order.publishing.listing.product is not None:
                product = order.publishing.listing.product
                order.publishing.listing.product = self._get_product_subclass(product, product.id)
            return order
        except model.DoesNotExist:
            return None
        except model.MultipleObjectsReturned:
            self._add_message("Multiple orders found for external_id %s" % external_id)
            raise model.MultipleObjectsReturned("Multiple orders found for external_id %s" % external_id)

    def get_publishing(self, incoming_order):
        try:
            model = self.get_publishing_model()
            # FIXME: Maye move this to publishing manager?
            publishing = model.objects.get(external_id=getattr(incoming_order, self.get_publishing_lookup_id()))
            if isinstance(publishing.listing, Listing) and isinstance(publishing.listing.product, Product):
                product = self._get_product_subclass(publishing.listing.product, publishing.listing.product.id)
                publishing.listing.product = product
            return publishing
        except model.DoesNotExist:
            self._add_message("No publishing %s found for order %s" % (incoming_order.item_id, incoming_order))
            return None

    def get_messages(self):
        return self._messages

    def is_modified(self, incoming, order):
        return False

    def is_new_order(self, incoming, order):
        if order is None:
            return True

        if not order.processed and not order.bypass:
            return True

        return False

    def is_order_to_process(self, incoming, order):
        # a new order should be processed*
        if order.bypass:
            return False

        # an existing order that has not been processed is threated as a new order
        if self.is_modified(incoming, order):
            return True

        return False

    def is_valid(self, incoming):
        """
        Validates incoming orders
        """
        return True

    def run(self, incoming):
        if self.is_valid(incoming):
            order = self.get_order(incoming)

            if self.is_new_order(incoming, order):
                self.process(incoming, None)
            elif self.is_order_to_process(incoming, order):
                self.process(incoming, order)

    def process(self, incoming, order):
        # get the related publishing
        publishing = self.get_publishing(incoming)

        self.action(publishing, incoming, order)

    def action(self, listing_item, incoming, order):
        """
        This method should update order with incoming data and perform actions
        """
        raise NotImplementedError

    def _add_message(self, message):
        self._messages.append(message)
