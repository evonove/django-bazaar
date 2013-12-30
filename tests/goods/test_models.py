#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from moneyed import Money

from bazaar.goods.models import Product, PriceList, ProductPrice
from bazaar.settings import bazaar_settings
from bazaar.warehouse.models import Stock

from ..base import BaseTestCase


class TestProduct(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")
        self.stock = Stock.objects.create(product=self.product)

    def tearDown(self):
        self.product.delete()
        self.stock.delete()

    def test_model(self):
        self.assertEqual(str(self.product), "a product")

    def test_product_price_empty(self):
        self.assertEqual(self.product.price, Money(0, "EUR"))

    def test_product_price(self):
        ProductPrice.objects.create(price=10, product=self.product,
                                    price_list=PriceList.objects.get_default())
        self.assertEqual(self.product.price, Money(10, "EUR"))

    def test_product_set_price(self):
        self.product.set_price(1)
        self.assertEqual(self.product.price, Money(1, "EUR"))

    def test_product_set_price_fails_when_product_unsaved(self):
        product = Product(name="new product")
        self.assertRaises(Product.UnsavedException, product.set_price, 2)

    def test_product_set_price_fails_when_default_price_list_doesnt_exists(self):
        bazaar_settings.DEFAULT_PRICE_LIST_ID = 1000
        self.assertRaises(PriceList.DoesNotExist, self.product.set_price, 2)
        bazaar_settings.DEFAULT_PRICE_LIST_ID = 1

    def test_product_cost_property(self):
        with self.assertRaises(NotImplementedError):
            self.product.cost


class TestPriceList(BaseTestCase):
    def setUp(self):
        self.price_list = PriceList.objects.create(name="foo")

    def tearDown(self):
        self.price_list.delete()

    def test_model(self):
        self.assertEqual("%s" % self.price_list, "foo")

    def test_manager(self):
        price_list = PriceList.objects.get_default()
        self.assertEqual(price_list.id, bazaar_settings.DEFAULT_PRICE_LIST_ID)

    def test_manager_fails_when_default_doesnt_exists(self):
        bazaar_settings.DEFAULT_PRICE_LIST_ID = 1000
        self.assertRaises(ImproperlyConfigured, PriceList.objects.get_default)
        bazaar_settings.DEFAULT_PRICE_LIST_ID = 1


class TestProductPrice(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")
        self.price_list = PriceList.objects.create(name="foo")
        self.product_price = ProductPrice.objects.create(
            price=10, product=self.product, price_list=self.price_list)

    def tearDown(self):
        self.product.delete()
        self.product_price.delete()
        self.price_list.delete()

    def test_model(self):
        self.assertEqual("%s" % self.product_price, "'a product' foo 10.00 €")