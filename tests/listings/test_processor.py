from __future__ import absolute_import
from __future__ import unicode_literals

from django.test import TestCase
import mock
from bazaar.listings.processor import OrderProcessor

from .. import factories as f


class TestProcessorGetOrder(TestCase):

    def setUp(self):
        self.order = f.OrderFactory()

    def test_get_order_does_not_fail_if_order_not_linked_to_a_publishing(self):
        processor = OrderProcessor()
        processor.order_lookup_id = 'external_id'
        incoming = mock.Mock()
        incoming.external_id = self.order.external_id
        self.assertEqual(processor.get_order(incoming), self.order)
