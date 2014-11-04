from __future__ import unicode_literals
import mock

from moneyed import Money

from bazaar.utils import money_to_default, send_to_staff

from .base import BaseTestCase


class TestUtils(BaseTestCase):
    def test_money_instances_are_converted_to_default_currency(self):
        money = money_to_default(Money(1.0, "USD"))
        self.assertEqual(money, Money(0.74, "EUR"))

    def test_non_money_values_are_returned_untouched(self):
        money = money_to_default(1.5)
        self.assertEqual(money, Money(1.5, "EUR"))

    @mock.patch('bazaar.utils.stored_messages.add_message_for')
    def test_send_to_staff_should_attach_tags_if_explicitly_passed(self, patched):
        send_to_staff('error', None, 'test_tag')
        arguments = patched.call_args[0]
        self.assertEqual(arguments[3], 'test_tag')

    @mock.patch('bazaar.utils.stored_messages.add_message_for')
    def test_send_to_staff_should_attach_empty_tags(self, patched):
        send_to_staff('error', None)
        arguments = patched.call_args[0]
        self.assertEqual(arguments[3], '')
