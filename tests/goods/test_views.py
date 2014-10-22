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


class TestBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', email='test@test.it', password='test')
        self.lost_and_found = f.LocationFactory(name='lost and found', slug='lost_and_found', type=4)
        self.storage = f.LocationFactory(name='storage', slug='storage', type=1)
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')

        # Move products to the warehouse
        api.move(self.lost_and_found, self.storage, self.product, 1, 5)
        api.move(self.lost_and_found, self.storage, self.product, 1, 10)


class TestProductListView(TestBase):

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

    def test_list_view_not_working_without_login(self):
        response = self.client.get(reverse('bazaar:product-list'))
        self.assertRedirects(response, '/accounts/login/?next=/products/')

    def test_list_view_no_products(self):
        self.client.login(username=self.user.username, password='test')
        self.product.delete()
        response = self.client.get(reverse('bazaar:product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        products = response.context_data['product_list']
        self.assertEqual(products.count(), 0)
        self.assertIn(_('No products found').encode(encoding='UTF-8'), response.content)

    def test_name_sort(self):
        f.ProductFactory(name='product2', price=2, description='the best you can have!')
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=-name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product2')

    def test_price_sort(self):
        f.ProductFactory(name='product2', price=1, description='the best you can have!')
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product2')

    def test_stock_sort(self):
        product2 = f.ProductFactory(name='product2', price=1, description='the best you can have!')
        api.move(self.lost_and_found, self.storage, product2, 1, 5)
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product2')

    def test_cost_sort(self):
        product2 = f.ProductFactory(name='product2', price=1, description='the best you can have!')
        api.move(self.lost_and_found, self.storage, product2, 1, 5000)
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=purchase_price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product1')

    def test_name_filter(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get('/products/?name=noproduct')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 0)

        response = self.client.get('/products/?name=product')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 1)

    def test_description_filter(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get('/products/?description=notthisone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 0)

        response = self.client.get('/products/?description=have!')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 1)

    def test_ean_filter(self):
        self.product.ean = 'myean'
        self.product.save()
        self.client.login(username=self.user.username, password='test')
        response = self.client.get('/products/?ean=abba')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 0)

        response = self.client.get('/products/?ean=ea')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 1)


class TestProductUpdateView(TestBase):

    def test_update_view_not_working_without_login(self):
        response = self.client.get(reverse('bazaar:product-update', kwargs={'pk': self.product.pk}))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('bazaar:product-update',
                                                                            kwargs={'pk': self.product.pk}))

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


class TestProductCreateView(TestBase):

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

    def test_create_view_not_working_without_login(self):
        data = {
            'price_0': 1,
            'price_1': 'EUR',
            'name': 'ModifiedName',
            'description': 'mydescription',
            'ean': None,
            'photo': '',
        }
        response = self.client.post(reverse('bazaar:product-create'), data=data)
        self.assertRedirects(response, '/accounts/login/?next=/products/new/')

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


class TestProductDetailView(TestBase):

    def test_detail_view_not_working_without_login(self):
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/products/%s/' % self.product.pk)

    def test_detail_view(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product = response.context_data['product']
        self.assertEqual(product.name, self.product.name)
        self.assertEqual(product.cost.amount, self.product.cost.amount)
        self.assertEqual(product.price.amount, self.product.price.amount)
        self.assertEqual(product.quantity, self.product.quantity)


class TestDeleteView(TestBase):

    def test_delete_view_not_working_without_login(self):
        response = self.client.get(reverse('bazaar:product-delete', kwargs={'pk': self.product.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/products/%s/delete/' % self.product.pk)

    def test_delete_view(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.post(reverse('bazaar:product-delete', args=(self.product.pk, )))
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)