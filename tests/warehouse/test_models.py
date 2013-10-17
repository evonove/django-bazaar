#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-bazaar
------------

Tests for `django-bazaar` modules module.
"""

from __future__ import unicode_literals

import unittest
import moneyed

from django.core.exceptions import ValidationError

from bazaar.warehouse.models import RealGood, Warehouse, Movement
from bazaar.settings import bazaar_settings

from ..models import Good


class TestModels(unittest.TestCase):
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

    def test_defaults_currency(self):
        warehouse = Warehouse.objects.create(name="a warehouse")
        good = Good.objects.create(name="a good")
        real_good = RealGood.objects.create(
            good=good, price=0.0, warehouse=warehouse)

        self.assertEqual(real_good.price.currency.code, "EUR")

    def test_realgood_str(self):
        expected = 'Real good 00000 - a good in a warehouse'
        self.assertEqual(expected, str(self.real_good))

    def test_movement_str(self):
        w = Warehouse.objects.create(name="a warehouse")
        g = Good.objects.create(name="a good")
        rg = RealGood.objects.create(price=1.0, original_price=1.0, uid='00000', warehouse=w,
                                     good=g)
        m = Movement.objects.create(quantity=1, agent='test', reason='testing purposes',
                                    warehouse=w, good=rg)
        expected = 'Movement from test in warehouse a warehouse: 1.0000'
        self.assertEqual(expected, str(m))

    def test_clean_realgood(self):
        bazaar_settings.DEFAULT_CURRENCY = moneyed.USD.code
        self.assertRaises(ValidationError, self.real_good.clean)
