from __future__ import unicode_literals, absolute_import

from django.core.management import call_command
from django.test import TestCase


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command("update_rates")
        super(BaseTestCase, cls).setUpClass()
