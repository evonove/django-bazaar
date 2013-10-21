#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from moneyed import Money

from bazaar.goods.models import Product, PriceList, ProductPrice
from bazaar.warehouse.models import Stock

from ..base import BaseTestCase


class TestProduct(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")

    def tearDown(self):
        self.product.delete()

    def test_model(self):
        self.assertEqual(str(self.product), "a product")

    def test_product_stock_property_empty(self):
        self.assertEqual(self.product.stock, 0)

    def test_product_stock_property(self):
        for i in range(10):
            stock = Stock.objects.create(
                product=self.product, price=0.0)
            stock.movements.create(quantity=1, agent="test")

        self.assertEqual(self.product.stock, 10)

    def test_product_price_property(self):
        ProductPrice.objects.create(price=10, product=self.product,
                                    price_list=PriceList.objects.get_default())
        self.assertEqual(self.product.price, Money(10, "EUR"))

    def test_product_cost_property(self):
        with self.assertRaises(NotImplementedError):
            self.product.cost
