from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from bazaar.goods.models import Product
from bazaar.warehouse import api
from tests import factories as f

from django.utils import timezone

FORCED_LOWER = -999999


class TestBase(TestCase):
    def setUp(self):
        self.time_ago = timezone.now()
        self.user = get_user_model().objects.create_user(username='test', email='test@test.it', password='test')
        self.lost_and_found = f.LocationFactory(name='lost and found', slug='lost_and_found', type=4)
        self.storage = f.LocationFactory(name='storage', slug='storage', type=1)
        self.output = f.LocationFactory(name='output', slug='output', type=2)
        self.customer = f.LocationFactory(name='customer', slug='customer', type=3)
        self.product1 = f.ProductFactory(name='product1', price=2, description='cheap!')
        self.product2 = f.ProductFactory(name='product2', price=20, description='not cheap!')
        self.product3 = f.ProductFactory(name='product3', price=200, description='really expensive!')

        # Move products to the warehouse
        api.move(self.lost_and_found, self.storage, self.product1, 1, 3)
        api.move(self.lost_and_found, self.storage, self.product2, 10, 30)
        api.move(self.lost_and_found, self.storage, self.product3, 100, 300)

        api.move(self.storage, self.output, self.product1, 1, 5)

        api.move(self.storage, self.output, self.product2, 1, 50)
        api.move(self.output, self.storage, self.product2, 1, 50)

        api.move(self.storage, self.output, self.product3, 5, 500)
        api.move(self.output, self.customer, self.product3, 2, 500)


class TestProductQuerySet(TestBase):

    def test_with_availability(self):
        product = Product.objects.with_availability(self.storage.id).get(pk=self.product1.id)
        self.assertEqual(product.availability, 0)

        product = Product.objects.with_availability(self.storage.id).get(pk=self.product2.id)
        self.assertEqual(product.availability, 10)

        product = Product.objects.with_availability(self.storage.id).get(pk=self.product3.id)
        self.assertEqual(product.availability, 95)

    def test_with_total_avr_cost(self):
        product = Product.objects.with_total_avr_cost((self.storage.id, self.output.id)).get(pk=self.product1.id)
        self.assertEqual(product.total_avr_cost, 5)

        product = Product.objects.with_total_avr_cost((self.storage.id, self.output.id)).get(pk=self.product2.id)
        self.assertEqual(product.total_avr_cost, 32)

        product = Product.objects.with_total_avr_cost((self.storage.id, self.output.id)).get(pk=self.product3.id)
        self.assertEqual(product.total_avr_cost, 306)

    def test_with_stock_quantity(self):
        product = Product.objects.with_stock_quantity(self.storage.id, self.output.id).get(pk=self.product1.id)
        self.assertEqual(product.stock_quantity, 1)

        product = Product.objects.with_stock_quantity(self.storage.id, self.output.id).get(pk=self.product2.id)
        self.assertEqual(product.stock_quantity, 10)

        product = Product.objects.with_stock_quantity(self.storage.id, self.output.id).get(pk=self.product3.id)
        self.assertEqual(product.stock_quantity, 98)

    def test_with_sold(self):
        product = Product.objects.with_sold(self.customer.id).get(pk=self.product1.id)
        self.assertEqual(product.sold, FORCED_LOWER)

        product = Product.objects.with_sold(self.customer.id).get(pk=self.product2.id)
        self.assertEqual(product.sold, FORCED_LOWER)

        product = Product.objects.with_sold(self.customer.id).get(pk=self.product3.id)
        self.assertEqual(product.sold, 2)

    def test_with_last_sold(self):
        present = timezone.now()
        product = Product.objects.with_last_sold(self.customer.id, self.time_ago, present=present)\
            .get(pk=self.product1.id)
        self.assertEqual(product.last_sold, FORCED_LOWER)

        product = Product.objects.with_last_sold(self.customer.id, self.time_ago, present=present)\
            .get(pk=self.product2.id)
        self.assertEqual(product.last_sold, FORCED_LOWER)

        product = Product.objects.with_last_sold(self.customer.id, self.time_ago, present=present)\
            .get(pk=self.product3.id)
        self.assertEqual(product.last_sold, 2)
