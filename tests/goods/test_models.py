#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from moneyed import Money

from bazaar.goods.models import Product, PriceList, ProductPrice
from bazaar.warehouse.models import RealGood, Warehouse

from ..base import BaseTestCase
from ..models import Good


class TestAbstractGood(BaseTestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(name="a warehouse")
        self.good = Good.objects.create(name="a good")
        self.real_good = RealGood.objects.create(price=1.0, original_price=1.0, uid='00000',
                                                 warehouse=self.warehouse, good=self.good)

    def tearDown(self):
        self.warehouse.delete()
        RealGood.objects.all().delete()
        Good.objects.all().delete()

    def test_goods_stock_property_empty(self):
        self.assertEqual(self.good.stock, 0)

    def test_goods_stock_property(self):
        for i in range(10):
            real_good = RealGood.objects.create(
                good=self.good, price=0.0, warehouse=self.warehouse)
            real_good.movements.create(quantity=1, agent="test", warehouse=self.warehouse)

        self.assertEqual(self.good.stock, 10)


class TestProduct(BaseTestCase):
    def setUp(self):
        self.product = Product.objects.create(name="a product")

    def tearDown(self):
        self.product.delete()

    def test_model(self):
        self.assertEqual(str(self.product), "a product")

    def test_product_price_property(self):
        ProductPrice.objects.create(price=10, product=self.product,
                                    price_list=PriceList.objects.get_default())
        self.assertEqual(self.product.price, Money(10, "EUR"))

    def test_product_cost_property(self):
        for i in range(10):
            self.product.elements.create(quantity=2, good=Good.objects.create(name="good"))

        self.assertEqual(self.product.cost, 20)
