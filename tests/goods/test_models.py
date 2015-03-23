#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.test import TestCase
from moneyed import Money

from bazaar.goods.models import Product, CompositeProduct
from bazaar.listings.models import Listing
from bazaar.settings import bazaar_settings
from ..factories import ProductFactory, StockFactory, ProductSetFactory


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
