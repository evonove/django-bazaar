from __future__ import unicode_literals

import unittest

from bazaar.warehouse.models import Warehouse


class TestManagement(unittest.TestCase):
    def test_default_warehouse_is_created(self):
        """
        An instance of warehouse with pk=1 is created post_syncdb
        """
        warehouse = Warehouse.objects.get(pk=1)
        self.assertTrue("Default", warehouse.name)
