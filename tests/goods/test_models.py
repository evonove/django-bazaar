#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from bazaar.goods.models import Product, PriceList, ProductPrice

from ..base import BaseTestCase


class TestProduct(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")

    def tearDown(self):
        self.product.delete()

    def test_model(self):
        self.assertEqual(str(self.product), "a product")

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