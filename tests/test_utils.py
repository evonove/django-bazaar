from __future__ import unicode_literals

from moneyed import Money

from bazaar.utils import convert_money_to_default_currency

from .base import BaseTestCase


class TestUtils(BaseTestCase):
    def test_money_instances_are_converted_to_default_currency(self):
        money = convert_money_to_default_currency(Money(1.0, "USD"))
        self.assertEqual(money, Money(0.74, "EUR"))

    def test_non_money_values_are_returned_untouched(self):
        money = convert_money_to_default_currency(1.5)
        self.assertEqual(money, 1.5)
