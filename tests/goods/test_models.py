#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from bazaar.goods.models import Product, PriceList, ProductPrice

from moneyed import Money

from ..base import BaseTestCase
from ..factories import ProductFactory, StockFactory


class TestProduct(TestCase):
    def setUp(self):
        self.product = ProductFactory()

    def tearDown(self):
        self.product.delete()

    def test_model(self):
        self.assertEqual("%s" % self.product, "a product")

    def test_product_cost_property(self):
        StockFactory(product=self.product, unit_price=10, quantity=10)
        StockFactory(product=self.product, unit_price=5, quantity=30)

        self.assertEqual(self.product.cost, Money(6.25, "EUR"))


class TestPriceList(BaseTestCase):
    def setUp(self):
        self.price_list = PriceList.objects.create(name="foo")

    def tearDown(self):
        self.price_list.delete()

    def test_model(self):
        self.assertEqual("%s" % self.price_list, "foo")


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