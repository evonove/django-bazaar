from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from ..utils import send_to_staff
from .processor import OrderProcessor


class OrderGrabber(object):
    processor_class = OrderProcessor

    def get_processor_class(self):
        if self.processor_class is None:
            raise ImproperlyConfigured("OrderGrabber requires 'processor_class' to be defined")

        return self.processor_class

    def get_processor(self):
        if not hasattr(self, "_processor"):
            processor_class = self.get_processor_class()
            self._processor = processor_class()

        return self._processor

    def get_messages(self):
        return self.get_processor().get_messages()

    def has_errors(self):
        return self.get_messages()

    def process(self, order):
        self.get_processor().run(order)

    def run(self, *args, **kwargs):
        for order in self.grab_orders(*args, **kwargs):
            self.process(order)

        self._notify_errors()

        return self.has_errors()

    def grab_orders(self, *args, **kwargs):
        """
        This method should yield a dict for each retrieved order
        """
        raise NotImplementedError

    def _notify_errors(self):
        send_to_staff(self.get_messages())
