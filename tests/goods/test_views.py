from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from bazaar.warehouse import api
from rest_framework import status
from rest_framework.reverse import reverse
from tests import factories as f


class TestProductView(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', email='test@test.it', password='test')
        self.lost_and_found = f.LocationFactory(name='lost and found', slug='lost_and_found', type=4)
        self.storage = f.LocationFactory(name='storage', slug='storage', type=1)
        self.product = f.ProductFactory(name='product1', price=2)

        # Move products to the warehouse
        api.move(self.lost_and_found, self.storage, self.product, 1, 5)
        api.move(self.lost_and_found, self.storage, self.product, 1, 10)

    def test_list_view(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 1)
        self.assertEqual(products[0].name, 'product1')
        self.assertEqual(products[0].cost.amount, 7.5)
        self.assertEqual(products[0].price.amount, 2)
        self.assertEqual(products[0].quantity, 2)