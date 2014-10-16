from __future__ import absolute_import
from __future__ import unicode_literals

from bazaar.listings.models import Store

from ..base import BaseTestCase


class TestAppInit(BaseTestCase):
    def tests_stores_created_on_app_init(self):
        """
        Tests that the stores configured in settings are created when the app is
        initialized
        """
        self.assertTrue(Store.objects.filter(slug="store1").exists())
        self.assertTrue(Store.objects.filter(slug="store2").exists())
