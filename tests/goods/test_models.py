#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
