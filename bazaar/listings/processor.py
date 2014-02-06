from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from .models import Order, Publishing


class OrderProcessor(object):
    order_model = Order
    publishing_model = Publishing

    def __init__(self):
        self._messages = []

    def get_order_model(self):
        if self.order_model is None:
            raise ImproperlyConfigured("OrderGrabber requires 'order_model' to be defined")

        return self.order_model

    def get_publishing_model(self):
        if self.publishing_model is None:
            raise ImproperlyConfigured("OrderGrabber requires 'publishing_model' to be defined")

        return self.publishing_model

    def get_previous_order(self, order):
        try:
            model = self.get_order_model()
            previous = model.objects.get(external_id=order.lineitem_id)
        except model.DoesNotExist:
            previous = model()

        return previous

    def get_publishing(self, order):
        try:
            model = self.get_publishing_model()
            publishing = model.objects.get(external_id=order.item_id)
        except model.DoesNotExist:
            self._add_message("No publishing %s found for order %s" %
                              (order.item_id, order.external_id))
            publishing = None

        return publishing

    def get_messages(self):
        return self._messages

    def is_modified(self, current, previous):
        # A new order should be processed
        if previous.pk is None:
            return True

    def skip_order(self, current, previous):
        # order is unchanged and has been already processed
        if not self.is_modified(current, previous) and previous.processed:
            return True

        return False

    def process(self, order):
        previous = self.get_previous_order(order)

        if self.skip_order(order, previous):
            return

        # get the related publishing
        publishing = self.get_publishing(order)

        # if order has been marked as bypass we should not process
        if not previous.bypass and publishing:
            previous_order = previous if previous.processed else None

            # TODO: to be enhanced
            for listing_item in publishing.listing.listing_sets.all():
                self.action(listing_item, publishing, order, previous_order)

            previous.processed = True
            previous.publishing = publishing

        self.update_previous_order(order, previous)

    def action(self, listing_item, publishing, current, previous):
        raise NotImplementedError

    def update_previous_order(self, current, previous):
        previous.external_id = current.lineitem_id
        previous.quantity = current.quantity
        previous.save()

    def _add_message(self, message):
        self._messages.append(message)
