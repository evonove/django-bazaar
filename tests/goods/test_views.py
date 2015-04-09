from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from bazaar.goods.models import Product
from django.utils.translation import ugettext as _
from bazaar.listings.models import Listing

from bazaar.warehouse import api
from rest_framework import status
from bazaar.warehouse.locations import get_storage, get_lost_and_found
from tests import factories as f
from tests.factories import PublishingFactory, ListingFactory, ProductFactory


class TestBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', email='test@test.it', password='test')
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')

        # Move products to the warehouse
        self.product.move(get_lost_and_found(), get_storage(), quantity=5)
        self.product.move(get_lost_and_found(), get_storage(), quantity=10)


class TestProductListView(TestBase):
    def test_list_view(self):
        """
        Test that list view works fine
        """
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
        """
        Test that trying to call the list view without beeing logged redirects to the login page
        """
        response = self.client.get(reverse('bazaar:product-list'))
        self.assertRedirects(response, '/accounts/login/?next=/products/')

    def test_list_view_no_products(self):
        """
        Test that a void list view displays "no products"
        """
        self.client.login(username=self.user.username, password='test')
        self.product.delete()
        response = self.client.get(reverse('bazaar:product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        products = response.context_data['product_list']
        self.assertEqual(products.count(), 0)
        self.assertIn(_('No products found').encode(encoding='UTF-8'), response.content)

    def test_name_sort(self):
        """
        Test that sort by name works correctly
        """
        f.ProductFactory(name='product2', price=2, description='the best you can have!')
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=-name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product2')

    def test_price_sort(self):
        """
        Test that sort by price works correctly
        """
        f.ProductFactory(name='product2', price=1, description='the best you can have!')
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product2')

    def test_stock_sort(self):
        """
        Test that sort by stock quantity works correctly
        """
        product2 = f.ProductFactory(name='product2', price=1, description='the best you can have!')
        product2.move(get_lost_and_found(), get_storage(), quantity=5)
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product2')

    def test_cost_sort(self):
        """
        Test that sort by cost works correctly
        """
        product2 = f.ProductFactory(name='product2', price=1, description='the best you can have!')
        api.move(get_lost_and_found(), get_storage(), product2, 1, 5000)
        self.client.login(username=self.user.username, password='test')
        response = self.client.get("/products/?&order_by=purchase_price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 2)
        self.assertEqual(products[0].name, 'product1')

    def test_name_filter(self):
        """
        Test that filter by name works correctly
        """
        self.client.login(username=self.user.username, password='test')
        response = self.client.get('/products/?name=noproduct')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 0)

        response = self.client.get('/products/?name=product')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.context_data['product_list']
        self.assertEqual(products.count(), 1)

    def test_ean_filter(self):
        """
        Test that filter by ean works correctly
        """
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
        """
        Test that the update view redirects to the login page if the user is not logged
        """
        response = self.client.get(reverse('bazaar:product-update', kwargs={'pk': self.product.pk}))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('bazaar:product-update',
                                                                            kwargs={'pk': self.product.pk}))

    def test_update_view(self):
        """
        Test that the update view works fine
        """
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

    def test_update_view_fails_with_incorrect_data(self):
        """
        Test that the update view fails with incorrect input
        """
        self.client.login(username=self.user.username, password='test')
        data = {
            'price_0': 'wrong data',
            'price_1': self.product.price.currency,
            'name': 'ModifiedName',
            'description': self.product.description,
            'ean': self.product.ean,
            'photo': self.product.photo.name,
        }
        response = self.client.post(reverse('bazaar:product-update', kwargs={'pk': self.product.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.name, self.product.name)


class TestProductCreateView(TestBase):
    def test_create_view(self):
        """
        Test that the create view works fine
        """
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
        product = Product.objects.get(name='ModifiedName')
        self.assertRedirects(response, '/products/%s/' % product.pk)

    def test_create_view_not_working_without_login(self):
        """
        Test that the create view redirects to the login page if the user is not logged
        """
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
        """
        Test that the create view doesn't work with negative price
        """
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
        """
        Test that the detail view redirects to the login page if the user is not logged
        """
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/products/%s/' % self.product.pk)

    def test_detail_view(self):
        """
        Test that the detail view works fine
        """
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product = response.context_data['product']
        self.assertEqual(product.name, self.product.name)
        self.assertEqual(product.cost.amount, self.product.cost.amount)
        self.assertEqual(product.price.amount, self.product.price.amount)
        self.assertEqual(product.quantity, self.product.quantity)

    def test_detail_view_img_being_shown(self):
        self.client.login(username=self.user.username, password='test')
        self.product.photo = 'product_photo.jpg'
        self.product.save()
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(('<img src="%s" class="img-thumbnail" width="100'
                       % self.product.photo.url).encode(encoding='UTF-8'), response.content)

    def test_detail_view_img_not_being_shown(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(b'<img ', response.content)

    def test_code_column_being_shown(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('<th>Code</th>'.encode(encoding='UTF-8'), response.content)

    def test_delete_button_disabled_if_there_is_a_publishing(self):
        one_item_listing = ListingFactory(product=self.product)
        PublishingFactory(listing=one_item_listing)

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(
            "Can't delete a product that was published at least once".encode(encoding='UTF-8'),
            response.content)

    def test_delete_button_enabled_if_no_publishing(self):
        ListingFactory(product=self.product)

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotIn(
            "Can't delete a product that was published at least once".encode(encoding='UTF-8'),
            response.content
        )

    def test_delete_button_enabled_if_product_has_no_listings(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotIn(
            "Can't delete a product that was published at least once".encode(encoding='UTF-8'),
            response.content
        )

    def test_delete_button_disabled_if_there_is_at_least_one_published_listing(self):
        product2 = ProductFactory()
        ListingFactory(product=self.product)
        two_item_listing = ListingFactory(products=[self.product, product2])

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotIn(
            "Can't delete a product that was published at least once".encode(encoding='UTF-8'),
            response.content
        )

        PublishingFactory(listing=two_item_listing)

        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(
            "Can't delete a product that was published at least once".encode(encoding='UTF-8'),
            response.content
        )


class TestDeleteView(TestBase):
    def test_delete_view_not_working_without_login(self):
        """
        Test that the delete view redirects to the login page if the user is not logged
        """
        response = self.client.get(reverse('bazaar:product-delete', kwargs={'pk': self.product.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/products/%s/delete/' % self.product.pk)

    def test_delete_view(self):
        """
        Test that the delete view works fine
        """
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.post(reverse('bazaar:product-delete', args=(self.product.pk, )))
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_view_can_only_be_called_if_product_is_deletable(self):
        one_item_listing = ListingFactory(product=self.product)
        publishing = PublishingFactory(listing=one_item_listing)

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(reverse('bazaar:product-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        publishing.delete()

        response = self.client.post(reverse('bazaar:product-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_delete_view_deletes_also_listing_in_common_with_other_products(self):
        """
        Test that associated listings are deleted too when using the delete view
        """
        product2 = ProductFactory()
        product3 = ProductFactory()

        one_item_listing = ListingFactory(product=self.product)
        listing_for_product2 = ListingFactory(product=product2)
        listing_for_product3 = ListingFactory(product=product3)
        multiple_item_listing = ListingFactory(products=[self.product, product2, product3])

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(reverse('bazaar:product-delete', args=(self.product.pk, )))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Check product has been deleted
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

        # Check that all associated listings have been deleted
        self.assertFalse(Listing.objects.filter(pk=one_item_listing.pk).exists())
        self.assertFalse(Listing.objects.filter(pk=multiple_item_listing.pk).exists())

        # Check that product2 and product3 listings have not been deleted
        self.assertTrue(Listing.objects.filter(pk=listing_for_product2.pk).exists())
        self.assertTrue(Listing.objects.filter(pk=listing_for_product3.pk).exists())

    def test_delete_view_deletes_only_listings_associated_to_the_product(self):
        """
        Test that other listings are not affected
        """
        product2 = ProductFactory()

        one_item_listing = ListingFactory(product=self.product)
        product2_listing = ListingFactory(product=product2)

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(reverse('bazaar:product-delete', args=(self.product.pk, )))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Check product has been deleted
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

        # Check that all associated listings have been deleted
        self.assertFalse(Listing.objects.filter(pk=one_item_listing.pk).exists())

        # Check that other listings are not affected
        self.assertTrue(Listing.objects.filter(pk=product2_listing.pk).exists())
