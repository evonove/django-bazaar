# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..base import BaseTestCase
from ..factories import StockFactory, MovementFactory


class TestStock(BaseTestCase):
    def setUp(self):
        self.stock = StockFactory(location__slug="storage")

    def test_model(self):
        self.assertEqual("%s" % self.stock, "Stock 'a product' at 'storage': 0.00 €")


class TestMovement(BaseTestCase):
    def setUp(self):
        self.movement = MovementFactory(from_location__slug="supplier", to_location__slug="storage")

    def test_movement_str(self):
        expected = "Movement 'a product' from 'supplier' to 'storage': 1"
        self.assertEqual(expected, "%s" % self.movement)
