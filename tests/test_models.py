#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-bazaar
------------

Tests for `django-bazaar` modules module.
"""

from __future__ import unicode_literals

import unittest

from bazaar.warehouse.models import RealGood, Warehouse

from .models import Good


class TestGoods(unittest.TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(name="a warehouse")

    def test_goods_stock_property_empty(self):
        good = Good.objects.create(name="a good")
        self.assertEqual(good.stock, 0)

    def test_goods_stock_property(self):
        good = Good.objects.create(name="a good")

        for i in range(10):
            real_good = RealGood.objects.create(
                good=good, price=0.0, currency="EUR", warehouse=self.warehouse)
            real_good.movements.create(quantity=1, agent="test", warehouse=self.warehouse)

        self.assertEqual(good.stock, 10)

    def tearDown(self):
        self.warehouse.delete()
        RealGood.objects.all().delete()
        Good.objects.delete()
