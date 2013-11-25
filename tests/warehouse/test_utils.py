from __future__ import unicode_literals

from django.test import TestCase

from bazaar.goods.models import Product
from bazaar.warehouse.exceptions import MovementException
from bazaar.warehouse.models import Movement, Stock
from bazaar.warehouse.utils import in_movement, out_movement


class TestMovementUtils(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="test product")

    def tearDown(self):
        self.product.delete()

        Stock.objects.all().delete()
        Movement.objects.all().delete()

    def test_in_movement_create_stock_with_code(self):
        in_movement(1, "test", "test", 10.0, self.product, "fake-code")
        self.assertTrue(Stock.objects.filter(code="fake-code", price=10.0).exists())

    def test_in_movement_create_stock_with_product(self):
        in_movement(1, "test", "test", 10.0, self.product)
        self.assertTrue(Stock.objects.filter(code="", product=self.product, price=10.0).exists())

    def test_in_movement_creates_different_stocks_without_code(self):
        in_movement(10, "test", "test", 10.0, self.product)
        in_movement(10, "test", "test", 5.0, self.product)
        self.assertTrue(Stock.objects.all().count(), 2)

    def test_in_movement_update_stocks_with_code(self):
        in_movement(10, "test", "test", 10.0, self.product, "fake-code")
        in_movement(10, "test", "test", 10.0, self.product, "fake-code")
        self.assertEqual(Stock.objects.get(code="fake-code").quantity, 20)

    def test_in_movement_raise_error_with_invalid_quantity(self):
        self.assertRaises(MovementException, in_movement, -1, "test", "test", 10.0, self.product)

    def test_out_movement_raise_error_with_invalid_quantity(self):
        with self.assertRaises(MovementException) as m:
            out_movement(-1, "test", "test", self.product)
        self.assertEqual(str(m.exception), "Quantity must be a positive amount")

    def test_out_movement_raise_error_when_product_and_code_missing(self):
        with self.assertRaises(MovementException) as m:
            out_movement(1, "test", "test")
        self.assertEqual(str(m.exception), "Movement out need at least a product or a code")

    def test_out_movement_raise_error_with_wrong_code(self):
        with self.assertRaises(MovementException) as m:
            out_movement(1, "test", "test", code="fake-code")
        self.assertEqual(str(m.exception), "Stock with code fake-code do not exists")

    def test_out_movement_raise_error_when_no_stock_exists(self):
        with self.assertRaises(MovementException) as m:
            out_movement(1, "test", "test", self.product)
        self.assertEqual(str(m.exception), "No stocks found for product 'test product'")

    def test_out_movement_with_code(self):
        in_movement(10, "test", "test", 10.0, self.product, code="fake-code")
        out_movement(9, "test", "test", code="fake-code")

        self.assertEqual(Stock.objects.get(code="fake-code").quantity, 1)

    def test_out_movement_with_product_single_stock(self):
        in_movement(10, "test", "test", 10.0, self.product)
        out_movement(9, "test", "test", self.product)

        self.assertEqual(Stock.objects.get(product=self.product).quantity, 1)

    def test_out_movement_with_product_multiple_stock(self):
        in_movement(5, "test", "test", 10.0, self.product)
        in_movement(5, "test", "test", 10.0, self.product)
        out_movement(9, "test", "test", self.product)

        stocks = Stock.objects.filter(product=self.product)
        self.assertEqual(stocks[0].quantity, 0)
        self.assertEqual(stocks[1].quantity, 1)

    def test_out_movement_with_product_multiple_stock_lower_quantity(self):
        in_movement(5, "test", "test", 10.0, self.product, code="fake-code")
        in_movement(5, "test", "test", 10.0, self.product)
        in_movement(5, "test", "test", 10.0, self.product)
        out_movement(12, "test", "test", self.product)

        stocks = Stock.objects.filter(product=self.product, code="")
        self.assertEqual(stocks[0].quantity, 0)
        self.assertEqual(stocks[1].quantity, -2)
        self.assertEqual(Stock.objects.get(code="fake-code").quantity, 5)
