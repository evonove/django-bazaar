from __future__ import unicode_literals

from django.core.management import call_command
from django.test import TestCase


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command("update_rates")
        super().setUpClass()
