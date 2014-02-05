# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bazaar.goods.models import Product
from bazaar.warehouse.models import Stock, Movement
from bazaar.warehouse.utils import in_movement
from bazaar.listings.models import Listing, ListingSet, Publishing, Store, Order

from moneyed import Money

from ..base import BaseTestCase


class TestStock(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")
        self.stock = Stock.objects.create(product=self.product)

    def tearDown(self):
        self.stock.delete()
        self.product.delete()

    def test_model(self):
        self.assertEqual("%s" % self.stock, "Stock 'a product' - 0.00 €")

    def test_price_is_converted_to_default_currency(self):
        self.stock.price = Money(1.0, "USD")
        self.stock.save()

        self.assertEqual(self.stock.price, Money(0.74, "EUR"))

    def test_defaults_currency(self):
        self.assertEqual(self.stock.price.currency.code, "EUR")


class TestMovement(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")
        self.stock = Stock.objects.create(product=self.product)
        self.movement = Movement.objects.create(
            quantity=1, agent="test", reason="testing purposes", stock=self.stock)

    def tearDown(self):
        self.product.delete()
        self.stock.delete()
        self.movement.delete()

    def test_movement_str(self):
        expected = "Movement 'a product' - testing purposes by test: 1.0000"
        self.assertEqual(expected, "%s" % self.movement)


class TestStockAvailability(BaseTestCase):
    def setUp(self):
        # Create a store
        self.store = Store.objects.create(name="store", slug="store")

        # create some product
        self.product_1 = Product.objects.create(name="product 1")
        self.product_2 = Product.objects.create(name="product 2")

        # and add some to stock
        in_movement(20, "test", "test", self.product_1, 1.0)
        in_movement(20, "test", "test", self.product_2, 1.0)

        # create related listings and publishings
        self.listing_1 = Listing.objects.create(title="listing 1")
        self.listing_2 = Listing.objects.create(title="listing 2")
        self.listing_3 = Listing.objects.create(title="listing 3")
        self.listing_4 = Listing.objects.create(title="listing 4")

        ListingSet.objects.create(product=self.product_1, listing=self.listing_1, quantity=1)
        ListingSet.objects.create(product=self.product_2, listing=self.listing_2, quantity=1)

        ListingSet.objects.create(product=self.product_1, listing=self.listing_3, quantity=2)
        ListingSet.objects.create(product=self.product_2, listing=self.listing_3, quantity=1)

        ListingSet.objects.create(product=self.product_1, listing=self.listing_4, quantity=1)
        ListingSet.objects.create(product=self.product_2, listing=self.listing_4, quantity=3)

        self.publishing_1 = Publishing.objects.create(listing=self.listing_1, store=self.store)
        self.publishing_2 = Publishing.objects.create(listing=self.listing_2, store=self.store)
        self.publishing_3 = Publishing.objects.create(listing=self.listing_3, store=self.store)
        self.publishing_4 = Publishing.objects.create(listing=self.listing_4, store=self.store)

        # create some orders
        Order.objects.create(publishing=self.publishing_1, store=self.store,
                             status=Order.ORDER_COMPLETED, quantity=1)
        Order.objects.create(publishing=self.publishing_1, store=self.store,
                             status=Order.ORDER_PENDING, quantity=2)

        Order.objects.create(publishing=self.publishing_2, store=self.store,
                             status=Order.ORDER_PENDING, quantity=1)
        Order.objects.create(publishing=self.publishing_2, store=self.store,
                             status=Order.ORDER_COMPLETED, quantity=2)

        Order.objects.create(publishing=self.publishing_3, store=self.store,
                             status=Order.ORDER_PENDING, quantity=1)
        Order.objects.create(publishing=self.publishing_3, store=self.store,
                             status=Order.ORDER_PENDING, quantity=3)

        Order.objects.create(publishing=self.publishing_4, store=self.store,
                             status=Order.ORDER_COMPLETED, quantity=2)
        Order.objects.create(publishing=self.publishing_4, store=self.store,
                             status=Order.ORDER_PENDING, quantity=2)

    def tearDown(self):
        self.store.delete()
        self.product_1.delete()
        self.product_2.delete()
        self.listing_1.delete()
        self.listing_2.delete()
        self.listing_3.delete()
        self.listing_4.delete()
        self.publishing_1.delete()
        self.publishing_2.delete()
        self.publishing_3.delete()
        self.publishing_4.delete()
        Order.objects.all().delete()

    def test_available_property_with_no_orders(self):
        Order.objects.all().delete()
        self.assertEqual(self.product_1.stock.available, 20)
        self.assertEqual(self.product_2.stock.available, 20)

    def test_available_property_is_correct(self):
        self.assertEqual(self.product_1.stock.available, 8)
        self.assertEqual(self.product_2.stock.available, 9)
