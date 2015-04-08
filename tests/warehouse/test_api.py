from __future__ import unicode_literals
from django.dispatch import receiver

from django.test import TestCase
from bazaar.settings import bazaar_settings

from bazaar.warehouse.exceptions import MovementException
from bazaar.warehouse.models import Movement, Stock, Location
from bazaar.warehouse.api import move, get_stock_price, get_stock_quantity

from moneyed import Money
from bazaar.warehouse.signals import lost_and_found_changed, supplier_changed, storage_changed, output_changed, customer_changed

from ..base import BaseTestCase
from ..factories import (ProductFactory, StorageFactory, SupplierFactory, StockFactory,
                         CustomerFactory, OutputFactory, LostFoundFactory, CompositeProductFactory, ProductSetFactory)


class TestMovementApi(BaseTestCase):
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


class TestSignalsApi(TestCase):
    def setUp(self):
        self.product = ProductFactory()
        self.storage = StorageFactory()
        self.supplier = SupplierFactory()
        self.customer = CustomerFactory()
        self.output = OutputFactory()
        self.lostfound = LostFoundFactory()

    def test_move_laf_to_supplier_launch_proper_signals(self):
        self.s_lostandfound_sender = None
        self.s_lostandfound_product = None

        @receiver(lost_and_found_changed)
        def lostandfound_listener(sender, product, **kwargs):
            self.s_lostandfound_sender = sender
            self.s_lostandfound_product = product

        self.s_supplier_sender = None
        self.s_supplier_product = None

        @receiver(supplier_changed)
        def supplier_listener(sender, product, **kwargs):
            self.s_supplier_sender = sender
            self.s_supplier_product = product

        quantity = 10
        price = Money(3, bazaar_settings.DEFAULT_CURRENCY)
        move(self.lostfound, self.supplier, self.product, quantity, price)
        lostandfound_stock = Stock.objects.get(location=self.lostfound, product=self.product)
        supplier_stock = Stock.objects.get(location=self.supplier, product=self.product)

        self.assertEqual(self.s_lostandfound_sender, lostandfound_stock)
        self.assertEqual(self.s_supplier_sender, supplier_stock)

        self.assertEqual(self.s_lostandfound_product, self.product)
        self.assertEqual(self.s_supplier_product, self.product)

        self.assertEqual(self.s_lostandfound_sender.quantity, -quantity)
        self.assertEqual(self.s_supplier_sender.quantity, quantity)

        self.assertEqual(self.s_supplier_sender.unit_price, price)

    def test_move_supplier_to_storage_launch_proper_signals(self):
        self.s_supplier_sender = None
        self.s_supplier_product = None

        @receiver(supplier_changed)
        def supplier_listener(sender, product, **kwargs):
            self.s_supplier_sender = sender
            self.s_supplier_product = product

        self.s_storage_sender = None
        self.s_storage_product = None

        @receiver(storage_changed)
        def storage_listener(sender, product, **kwargs):
            self.s_storage_sender = sender
            self.s_storage_product = product

        quantity = 20
        price = Money(3, bazaar_settings.DEFAULT_CURRENCY)
        move(self.supplier, self.storage, self.product, quantity, price)
        supplier_stock = Stock.objects.get(location=self.supplier, product=self.product)
        storage_stock = Stock.objects.get(location=self.storage, product=self.product)

        self.assertEqual(self.s_supplier_sender, supplier_stock)
        self.assertEqual(self.s_storage_sender, storage_stock)

        self.assertEqual(self.s_supplier_product, self.product)
        self.assertEqual(self.s_storage_product, self.product)

        self.assertEqual(self.s_supplier_sender.quantity, -quantity)
        self.assertEqual(self.s_storage_sender.quantity, quantity)

        self.assertEqual(self.s_storage_sender.unit_price, price)

    def test_move_storage_to_output_launch_proper_signals(self):
        self.s_storage_sender = None
        self.s_storage_product = None

        @receiver(storage_changed)
        def storage_listener(sender, product, **kwargs):
            self.s_storage_sender = sender
            self.s_storage_product = product

        self.s_output_sender = None
        self.s_output_product = None

        @receiver(output_changed)
        def output_listener(sender, product, **kwargs):
            self.s_output_sender = sender
            self.s_output_product = product

        quantity = 20
        price = Money(3, bazaar_settings.DEFAULT_CURRENCY)
        move(self.storage, self.output, self.product, quantity, price)
        storage_stock = Stock.objects.get(location=self.storage, product=self.product)
        output_stock = Stock.objects.get(location=self.output, product=self.product)

        self.assertEqual(self.s_output_sender, output_stock)
        self.assertEqual(self.s_storage_sender, storage_stock)

        self.assertEqual(self.s_output_product, self.product)
        self.assertEqual(self.s_storage_product, self.product)

        self.assertEqual(self.s_output_sender.quantity, quantity)
        self.assertEqual(self.s_storage_sender.quantity, -quantity)

        self.assertEqual(self.s_output_sender.unit_price, price)

    def test_move_output_to_customer_launch_proper_signals(self):
        self.s_output_sender = None
        self.s_output_product = None

        @receiver(output_changed)
        def output_listener(sender, product, **kwargs):
            self.s_output_sender = sender
            self.s_output_product = product

        self.s_customer_sender = None
        self.s_customer_product = None

        @receiver(customer_changed)
        def customer_listener(sender, product, **kwargs):
            self.s_customer_sender = sender
            self.s_customer_product = product


        quantity = 20
        price = Money(3, bazaar_settings.DEFAULT_CURRENCY)
        move(self.output, self.customer, self.product, quantity, price)
        output_stock = Stock.objects.get(location=self.output, product=self.product)
        customer_stock = Stock.objects.get(location=self.customer, product=self.product)

        self.assertEqual(self.s_output_sender, output_stock)
        self.assertEqual(self.s_customer_sender, customer_stock)

        self.assertEqual(self.s_output_product, self.product)
        self.assertEqual(self.s_customer_product, self.product)

        self.assertEqual(self.s_output_sender.quantity, -quantity)
        self.assertEqual(self.s_customer_sender.quantity, quantity)

        self.assertEqual(self.s_customer_sender.unit_price, price)


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

#
# class TestStockApi(TestCase):
#     def setUp(self):
#         self.product_a = ProductFactory()
#         self.stock_a = StockFactory(product=self.product_a, unit_price=2.0, quantity=30)
#         self.stock_b = StockFactory(product=self.product_a, unit_price=4.0, quantity=10)
#         self.stock_c = StockFactory(product=self.product_a, unit_price=3.0, quantity=10)
#
#     def test_get_stock_quantity(self):
#         quantity = get_stock_quantity(self.product_a, Location.LOCATION_STORAGE)
#         self.assertEqual(quantity, 50)
#
#     def test_get_stock_quantity_from_empty_stock(self):
#         quantity = get_stock_quantity(ProductFactory(), Location.LOCATION_STORAGE)
#         self.assertEqual(quantity, 0)
#
#     def test_get_stock_price(self):
#         price = get_stock_price(self.product_a, Location.LOCATION_STORAGE)
#         self.assertEqual(price, Money(2.6, "EUR"))
#
#     def test_get_stock_price_no_stocks(self):
#         price = get_stock_price(ProductFactory(), Location.LOCATION_STORAGE)
#         self.assertEqual(price, Money(0, "EUR"))
#
#     def test_get_stock_price_empty_stocks(self):
#         product = ProductFactory()
#         StockFactory(product=product, unit_price=2.0, quantity=0)
#         StockFactory(product=product, unit_price=4.0, quantity=0)
#         StockFactory(product=product, unit_price=3.0, quantity=0)
#
#         with self.assertNumQueries(1):
#             price = get_stock_price(product, Location.LOCATION_STORAGE)
#
#         self.assertEqual(price, Money(3.0, "EUR"))


class TestStockApi(TestCase):
    def setUp(self):
        self.product_a = ProductFactory()
        self.stock_a = StockFactory(product=self.product_a, unit_price=2.0, quantity=30)
        self.stock_b = StockFactory(product=self.product_a, unit_price=4.0, quantity=10)
        self.stock_c = StockFactory(product=self.product_a, unit_price=3.0, quantity=10)

        self.product_b = ProductFactory()
        self.stock_d = StockFactory(product=self.product_b, unit_price=1.0, quantity=10)

        self.composite = CompositeProductFactory()
        self.product_set_a = ProductSetFactory(product=self.product_a, composite=self.composite, quantity=2)
        self.product_set_b = ProductSetFactory(product=self.product_b, composite=self.composite, quantity=1)

    def test_get_stock_quantity_for_single_product(self):
        quantity = get_stock_quantity(self.product_a, Location.LOCATION_STORAGE)
        self.assertEqual(quantity, 50)

    def test_get_stock_quantity_for_composite(self):
        quantity = get_stock_quantity(self.composite, Location.LOCATION_STORAGE)
        self.assertEqual(quantity, 10)

    def test_get_stock_quantity_from_empty_stock(self):
        quantity = get_stock_quantity(ProductFactory(), Location.LOCATION_STORAGE)
        self.assertEqual(quantity, 0)

    def test_get_stock_price(self):
        price = get_stock_price(self.product_a, Location.LOCATION_STORAGE)
        self.assertEqual(price, Money(2.6, "EUR"))

    def test_get_stock_price_no_stocks(self):
        price = get_stock_price(ProductFactory(), Location.LOCATION_STORAGE)
        self.assertEqual(price, Money(0, "EUR"))

    def test_get_stock_price_empty_stocks(self):
        product = ProductFactory()
        StockFactory(product=product, unit_price=2.0, quantity=0)
        StockFactory(product=product, unit_price=4.0, quantity=0)
        StockFactory(product=product, unit_price=3.0, quantity=0)

        with self.assertNumQueries(1):
            price = get_stock_price(product, Location.LOCATION_STORAGE)

        self.assertEqual(price, Money(3.0, "EUR"))
