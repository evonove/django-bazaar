#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.test import TestCase
from moneyed import Money

from bazaar.goods.models import Product, CompositeProduct
from bazaar.listings.models import Listing
from bazaar.settings import bazaar_settings
from bazaar.warehouse.api import get_storage_quantity
from ..factories import ProductFactory, StockFactory, ProductSetFactory, CompositeProductFactory, LocationFactory, \
    StorageFactory, LostFoundFactory, OutputFactory
from market.locations import get_lost_and_found, get_storage


class TestProduct(TestCase):

    def setUp(self):
        self.old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = True

    def test_model(self):
        self.product = ProductFactory(ean="12345678")
        self.assertEqual("%s" % self.product, "a product")

    def test_product_cost_property(self):
        self.product = ProductFactory(ean="12345678")
        StockFactory(product=self.product, unit_price=10, quantity=10)
        StockFactory(product=self.product, unit_price=5, quantity=30)

        self.assertEqual(self.product.cost, Money(6.25, "EUR"))

    def test_product_ean_property(self):
        """
        Checks that the ean property is set
        """
        self.product = ProductFactory(ean="12345678")
        self.assertEqual(self.product.ean, "12345678")

    def test_product_code_property(self):
        """
        Checks that the ean property is set
        """
        self.product = ProductFactory(code="thisisacode")
        self.assertEqual(self.product.code, "thisisacode")

    def test_ean_should_not_be_none(self):
        self.product = ProductFactory(ean="12345678")
        self.assertRaises(Exception, ProductFactory, ean=None)

    def test_product_photo_property(self):
        self.product = ProductFactory(ean="12345678")
        self.product.photo = 'test.jpg'
        self.product.save()

        self.assertEqual(self.product.photo.name, 'test.jpg')

    def test_on_product_creation_a_listing_should_be_created(self):
        """
        Tests that on product creation a new 1x listing is created.
        """
        self.assertFalse(Listing.objects.all().exists())

        product = ProductFactory()
        listings = Listing.objects.filter(product=product)

        self.assertEqual(listings.count(), 1)

    def test_that_a_listing_is_created_only_during_product_creation(self):
        """
        Test that a listing is created only when saving a product for the first time (creation).
        On subsequent saves, no more listings should be created.
        """
        self.assertFalse(Listing.objects.all().exists())

        product = ProductFactory()
        listings = Listing.objects.filter(product=product)

        self.assertEqual(listings.count(), 1)

        product.name = "test"
        product.save()

        listings = Listing.objects.filter(product=product)
        self.assertEqual(listings.count(), 1)

    def tearDown(self):
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = self.old_setting_value


class TestCompositeProduct(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name='Product1')
        self.product2 = Product.objects.create(name='Product2')
        self.composite_product = CompositeProduct.objects.create(name='Composite')
        ProductSetFactory(composite=self.composite_product, product=self.product1, quantity=1)
        ProductSetFactory(composite=self.composite_product, product=self.product2, quantity=1)

    def test_products_added_to_composite_product(self):
        self.assertIn(self.product1, self.composite_product.products.all())
        self.assertIn(self.product2, self.composite_product.products.all())


class TestProductMovements(TestCase):
    def setUp(self):
        self.storage = StorageFactory()
        self.lost_and_found = LostFoundFactory()
        self.output = OutputFactory()

        self.product_1 = ProductFactory()
        self.product_2 = ProductFactory()

        self.composite_1 = CompositeProductFactory()
        self.composite_2 = CompositeProductFactory()

        self.ps_1 = ProductSetFactory(product=self.product_1, composite=self.composite_1, quantity=1)
        self.ps_2 = ProductSetFactory(product=self.product_1, composite=self.composite_2, quantity=2)
        self.ps_3 = ProductSetFactory(product=self.product_2, composite=self.composite_2, quantity=3)

    def test_add_one_product_creates_stock_only_for_composite_1(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=1)

        self.assertEqual(get_storage_quantity(product=self.composite_1), 1)
        self.assertEqual(get_storage_quantity(product=self.composite_2), 0)
        self.assertEqual(get_storage_quantity(product=self.product_1), 1)

    def test_add_more_products_creates_correct_stocks(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=2)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, quantity=3)

        self.assertEqual(get_storage_quantity(product=self.composite_1), 2)
        self.assertEqual(get_storage_quantity(product=self.composite_2), 1)
        self.assertEqual(get_storage_quantity(product=self.product_1), 2)
        self.assertEqual(get_storage_quantity(product=self.product_2), 3)

    def test_remove_products_update_composite_quantity_correctly(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=2)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, quantity=3)

        self.assertEqual(get_storage_quantity(product=self.composite_1), 2)
        self.assertEqual(get_storage_quantity(product=self.composite_2), 1)

        self.product_1.move(from_location=self.storage, to_location=self.output)

        self.assertEqual(get_storage_quantity(product=self.composite_1), 1)
        self.assertEqual(get_storage_quantity(product=self.composite_2), 0)

    def test_move_composite_products(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=2)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, quantity=3)

        self.assertEqual(get_storage_quantity(product=self.composite_1), 2)
        self.assertEqual(get_storage_quantity(product=self.composite_2), 1)

        self.composite_1.move(from_location=self.storage, to_location=self.output)

        self.assertEqual(get_storage_quantity(product=self.composite_1), 1)
        self.assertEqual(get_storage_quantity(product=self.composite_2), 0)
        self.assertEqual(get_storage_quantity(product=self.product_1), 1)

    def test_move_composite_products_negative_quantities(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=2)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, quantity=3)

        self.assertEqual(get_storage_quantity(product=self.composite_1), 2)
        self.assertEqual(get_storage_quantity(product=self.composite_2), 1)

        self.composite_1.move(from_location=self.storage, to_location=self.output, quantity=3)

        # FIXME: Should composite product stocks go under 0??
        self.assertEqual(get_storage_quantity(product=self.composite_1), -1)
        self.assertEqual(get_storage_quantity(product=self.composite_2), -1)
        self.assertEqual(get_storage_quantity(product=self.product_1), -1)
