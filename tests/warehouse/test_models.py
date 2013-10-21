from __future__ import unicode_literals

from bazaar.goods.models import Product
from bazaar.warehouse.models import Stock, Movement

from moneyed import Money

from ..base import BaseTestCase


class TestRealGood(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")
        self.stock = Stock.objects.create(code="fake-code", product=self.product)

    def tearDown(self):
        self.stock.delete()
        self.product.delete()

    def test_model(self):
        self.assertEqual(str(self.stock), "Stock fake-code - 'a product'")

    def test_price_is_converted_to_default_currency(self):
        self.stock.price = Money(1.0, "USD")
        self.stock.save()

        self.assertEqual(self.stock.price, Money(0.74, "EUR"))
        self.assertEqual(self.stock.original_price, Money(1.0, "USD"))

    def test_defaults_currency(self):
        self.assertEqual(self.stock.price.currency.code, "EUR")


class TestMovement(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")
        self.stock = Stock.objects.create(code="fake-code", product=self.product)
        self.movement = Movement.objects.create(
            quantity=1, agent="test", reason="testing purposes", stock=self.stock)

    def tearDown(self):
        self.product.delete()
        self.stock.delete()
        self.movement.delete()

    def test_movement_str(self):
        expected = "Movement Stock fake-code - 'a product' - testing purposes by test: 1.0000"
        self.assertEqual(expected, str(self.movement))
