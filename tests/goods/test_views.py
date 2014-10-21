from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from bazaar.goods.models import Product
from django.utils.translation import ugettext as _

from bazaar.warehouse import api
from rest_framework import status
from tests import factories as f


class TestProductView(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', email='test@test.it', password='test')
        self.lost_and_found = f.LocationFactory(name='lost and found', slug='lost_and_found', type=4)
        self.storage = f.LocationFactory(name='storage', slug='storage', type=1)
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')

        # Move products to the warehouse
        api.move(self.lost_and_found, self.storage, self.product, 1, 5)
        api.move(self.lost_and_found, self.storage, self.product, 1, 10)

    def test_list_view(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 1)
        self.assertEqual(products[0].name, self.product.name)
        self.assertEqual(products[0].cost.amount, self.product.cost.amount)
        self.assertEqual(products[0].price.amount, self.product.price.amount)
        self.assertEqual(products[0].quantity, self.product.quantity)

    def test_list_view_no_products(self):
        self.client.login(username=self.user.username, password='test')
        self.product.delete()
        response = self.client.get(reverse('bazaar:product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        products = response.context_data['product_list']
        self.assertEqual(products.count(), 0)
        self.assertIn(_('No products found'), response.content)

    def test_update_view(self):
        self.client.login(username=self.user.username, password='test')
        data = {
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency,
            'name': 'ModifiedName',
            'description': self.product.description,
            'ean': self.product.ean,
            'photo': self.product.photo.name,
        }
        response = self.client.post(reverse('bazaar:product-update', kwargs={'pk': self.product.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.name, 'ModifiedName')

    def test_create_view(self):
        self.client.login(username=self.user.username, password='test')
        data = {
            'price_0': 1,
            'price_1': 'EUR',
            'name': 'ModifiedName',
            'description': 'mydescription',
            'ean': None,
            'photo': '',
        }
        response = self.client.post(reverse('bazaar:product-create'), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIsNotNone(Product.objects.get(name='ModifiedName'))

    def test_create_view_not_working_with_negative_price(self):
        self.client.login(username=self.user.username, password='test')
        data = {
            'price_0': -1,
            'price_1': 'EUR',
            'name': 'ModifiedName',
            'description': 'mydescription',
            'ean': None,
            'photo': '',
        }
        response = self.client.post(reverse('bazaar:product-create'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.filter(name='ModifiedName').count(), 0)

    def test_detail_view(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product = response.context_data['product']
        self.assertEqual(product.name, self.product.name)
        self.assertEqual(product.cost.amount, self.product.cost.amount)
        self.assertEqual(product.price.amount, self.product.price.amount)
        self.assertEqual(product.quantity, self.product.quantity)
