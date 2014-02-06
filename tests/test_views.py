from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from .base import BaseTestCase


class TestViews(BaseTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="123456")

    def tearDown(self):
        self.user.delete()

    def test_home_view(self):
        response = self.client.get(reverse("bazaar:home"))
        self.assertContains(response, "This is the home")

    def test_login_redirect_home(self):
        self.client.login(username="test", password="123456")

        response = self.client.get(reverse("bazaar:login"))
        self.assertRedirects(response, reverse("bazaar:home"))
