from __future__ import unicode_literals

import unittest

from bazaar.warehouse.models import Warehouse
from bazaar.settings import bazaar_settings


class TestWarehouse(unittest.TestCase):
    def test_model(self):
        warehouse = Warehouse(name="a warehouse")
        self.assertEqual(str(warehouse), "a warehouse")

    def test_get_default_return_default_warehouse(self):
        warehouse = Warehouse.objects.get_default()
        self.assertEqual(bazaar_settings.DEFAULT_WAREHOUSE_ID, warehouse.id)
