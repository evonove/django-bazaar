from __future__ import unicode_literals

import unittest

from django.core.management import call_command


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        call_command("update_rates")
