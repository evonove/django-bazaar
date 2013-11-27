from __future__ import unicode_literals

from django.test import TestCase

from bazaar.goods.models import Product
from bazaar.warehouse.exceptions import MovementException
from bazaar.warehouse.models import Movement, Stock
from bazaar.warehouse.utils import in_movement, out_movement

from moneyed import Money


class TestMovementUtils(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="test product")

    def tearDown(self):
        self.product.delete()

        Stock.objects.all().delete()
        Movement.objects.all().delete()

    def test_in_movement_raise_error_with_invalid_quantity(self):
        self.assertRaises(MovementException, in_movement, -1, "test", "test", self.product, 10.0)

    def test_in_movement_create_stock(self):
        in_movement(1, "test", "test", self.product, 10.0)
        self.assertTrue(Stock.objects.filter(product=self.product, price=10.0).exists())

    def test_in_movement_alter_stock_price(self):
        in_movement(10, "test", "test", self.product, 10.0)
        in_movement(10, "test", "test", self.product, 5.0)
        self.assertEqual(Stock.objects.get(product=self.product).price, Money(7.5, "EUR"))

    def test_in_movement_no_price_do_not_alter_stock_price(self):
        in_movement(10, "test", "test", self.product, 10.0)
        in_movement(10, "test", "test", self.product, 5.0)
        in_movement(10, "test", "test", self.product)
        self.assertEqual(Stock.objects.get(product=self.product).price, Money(7.5, "EUR"))

    def test_out_movement_raise_error_with_invalid_quantity(self):
        with self.assertRaises(MovementException) as m:
            out_movement(-1, "test", "test", self.product)
        self.assertEqual("%s" % m.exception, "Quantity must be a positive amount")

    def test_out_movement_raise_error_when_no_stock_exists(self):
        with self.assertRaises(MovementException) as m:
            out_movement(1, "test", "test", self.product)
        self.assertEqual("%s" % m.exception, "No stock found for product 'test product'")

    def test_out_movement(self):
        in_movement(10, "test", "test", self.product, 10.0)
        out_movement(9, "test", "test", self.product)

        stock = Stock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, 1)

    def test_out_movement_multiple_movements(self):
        in_movement(5, "test", "test", self.product, 10.0)
        in_movement(5, "test", "test", self.product, 10.0)
        out_movement(9, "test", "test", self.product)

        stock = Stock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, 1)

    def test_out_movement_lower_quantity(self):
        in_movement(5, "test", "test", self.product, 10.0)
        in_movement(5, "test", "test", self.product, 10.0)
        out_movement(12, "test", "test", self.product)

        stock = Stock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, -2)
