from __future__ import unicode_literals

from django.test import TestCase

from bazaar.warehouse.exceptions import MovementException
from bazaar.warehouse.models import Movement, Stock
from bazaar.warehouse.api import move

from moneyed import Money

from ..factories import (ProductFactory, StorageFactory, SupplierFactory,
                         CustomerFactory, OutputFactory, LostFoundFactory)


class TestMovementApi(TestCase):
    def setUp(self):
        self.product = ProductFactory()
        self.storage = StorageFactory()
        self.supplier = SupplierFactory()
        self.customer = CustomerFactory()
        self.output = OutputFactory()
        self.lostfound = LostFoundFactory()

    def test_move_raise_error_with_invalid_quantity(self):
        with self.assertRaises(MovementException):
            move(self.supplier, self.storage, self.product, -1, 1.0)

    def test_move_raise_error_with_invalid_data(self):
        with self.assertRaises(MovementException):
            move(None, None, self.product, 10, 1.0)

    def test_movement_is_created(self):
        self.assertFalse(Movement.objects.filter(
            from_location=self.supplier, to_location=self.storage).exists())

        move(self.supplier, self.storage, self.product, 10, 1.0)

        self.assertTrue(Movement.objects.filter(
            from_location=self.supplier, to_location=self.storage).exists())

    def test_movement_converts_currency(self):
        move(self.supplier, self.storage, self.product, 10, Money(1.0, "USD"))

        movement = Movement.objects.get(from_location=self.supplier, to_location=self.storage)

        self.assertEqual(movement.unit_price, Money(0.74, "EUR"))
        self.assertEqual(movement.original_unit_price, Money(1.0, "USD"))


class TestStock(TestCase):
    def setUp(self):
        self.product = ProductFactory()
        self.storage = StorageFactory()
        self.supplier = SupplierFactory()
        self.customer = CustomerFactory()
        self.output = OutputFactory()
        self.lostfound = LostFoundFactory()

    def test_stocks_are_created_on_move(self):
        self.assertFalse(Stock.objects.filter(location=self.supplier, product=self.product).exists())
        self.assertFalse(Stock.objects.filter(location=self.storage, product=self.product).exists())

        move(self.supplier, self.storage, self.product, 10, 1.0)

        self.assertTrue(Stock.objects.filter(location=self.supplier, product=self.product).exists())
        self.assertTrue(Stock.objects.filter(location=self.storage, product=self.product).exists())

    def test_stocks_quantity_updated_on_move(self):
        move(self.supplier, self.storage, self.product, 10, 1.0)
        move(self.supplier, self.storage, self.product, 10, 1.0)
        move(self.storage, self.output, self.product, 10, 1.0)
        move(self.output, self.storage, self.product, 5, 1.0)
        move(self.storage, self.supplier, self.product, 2, 1.0)

        supplier_stock = Stock.objects.get(location=self.supplier, product=self.product)
        storage_stock = Stock.objects.get(location=self.storage, product=self.product)
        output_stock = Stock.objects.get(location=self.output, product=self.product)

        self.assertEqual(supplier_stock.quantity, -18)
        self.assertEqual(storage_stock.quantity, 13)
        self.assertEqual(output_stock.quantity, 5)

    def test_stocks_price_updated_on_move(self):
        move(self.supplier, self.storage, self.product, 10, 1.0)
        move(self.supplier, self.storage, self.product, 10, 0.5)
        move(self.supplier, self.storage, self.product, 20, 0.4)
        move(self.storage, self.output, self.product, 1, 2.5)
        move(self.storage, self.output, self.product, 2, 2.0)
        move(self.storage, self.output, self.product, 5, 1.5)

        supplier_stock = Stock.objects.get(location=self.supplier, product=self.product)
        storage_stock = Stock.objects.get(location=self.storage, product=self.product)
        output_stock = Stock.objects.get(location=self.output, product=self.product)

        self.assertEqual(supplier_stock.unit_price, Money(0, "EUR"))
        self.assertEqual(storage_stock.unit_price, Money(0.575, "EUR"))
        self.assertEqual(output_stock.unit_price, Money(1.75, "EUR"))
