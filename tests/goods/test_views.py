from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.test import TestCase
from bazaar.goods.models import Product
from django.utils.translation import ugettext as _
from bazaar.listings.models import Listing, ListingSet

from bazaar.warehouse import api
from rest_framework import status
from tests import factories as f
from tests.factories import PublishingFactory, ListingFactory, ProductFactory, ListingSetFactory


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
        api.move(self.lost_and_found, self.storage, product2, 1, 5)
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
        api.move(self.lost_and_found, self.storage, product2, 1, 5000)
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
        one_item_listing = Listing.objects.create(title=self.product.name, description=self.product.description)
        ListingSet.objects.create(listing=one_item_listing, product=self.product, quantity=1)
        PublishingFactory(listing=one_item_listing)

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(
            "Can't delete a product that was published at least once".encode(encoding='UTF-8'),
            response.content)

    def test_delete_button_enabled_if_no_publishing(self):
        one_item_listing = Listing.objects.create(title=self.product.name, description=self.product.description)
        ListingSet.objects.create(listing=one_item_listing, product=self.product, quantity=1)

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
        product2 = Product.objects.create(name="another product", description="another description")
        one_item_listing = Listing.objects.create(title=self.product.name, description=self.product.description)
        two_item_listing = Listing.objects.create(title="2x1", description="buy 2 for 1")
        ListingSet.objects.create(listing=one_item_listing, product=self.product, quantity=1)
        ListingSet.objects.create(listing=two_item_listing, product=self.product, quantity=1)
        ListingSet.objects.create(listing=two_item_listing, product=product2, quantity=4)

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
        """
        Test that the product has associated publishings
        """
        one_item_listing = ListingFactory(title=self.product.name, description=self.product.description)
        ListingSetFactory(listing=one_item_listing, product=self.product, quantity=1)
        publishing = PublishingFactory(listing=one_item_listing)

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        publishing.delete()

        response = self.client.get(reverse('bazaar:product-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_view_deletes_also_listing_in_common_with_other_products(self):
        """
        Test that associated listings are deleted too when using the delete view
        """
        one_item_listing = ListingFactory(title=self.product.name, description=self.product.description)
        ListingSetFactory(listing=one_item_listing, product=self.product, quantity=1)

        product2 = ProductFactory(name="product 2", price=3, description="another product")
        listing_for_product2 = ListingFactory(title=product2.name, description=product2.description)
        ListingSetFactory(listing=listing_for_product2, product=product2, quantity=1)

        product3 = ProductFactory(name="product 3", description="yet another product")
        listing_for_product3 = ListingFactory(title=product3.name, description=product3.description)
        ListingSetFactory(listing=listing_for_product3, product=product3, quantity=1)

        multiple_item_listing = ListingFactory(title="product1 + product2 + product3", description="products bundle")
        ListingSetFactory(listing=multiple_item_listing, product=self.product)
        ListingSetFactory(listing=multiple_item_listing, product=product2)
        ListingSetFactory(listing=multiple_item_listing, product=product3)

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_listings_id = list(self.product.listings.values_list('id', flat=True))

        # Check Product.DoesNotExist not thrown
        Product.objects.get(id=self.product.id)

        self.client.post(reverse('bazaar:product-delete', args=(self.product.pk, )))

        # Check product has been deleted
        self.assertRaises(Product.DoesNotExist, Product.objects.get, **{'id': self.product.id})

        # Check that all associated listings have been deleted
        self.assertEqual(len(Listing.objects.filter(id__in=product_listings_id)), 0)

        self.assertEqual(len(Listing.objects.annotate(Count('products')).filter(products__count=0)), 0,
                         'There is at least one unassigned listing')

        # Check that common listing has been deleted
        self.assertRaises(Listing.DoesNotExist, Listing.objects.get, **{'pk': multiple_item_listing.pk})

        # Check that product2 and product3 listings have not been deleted
        Listing.objects.get(pk=listing_for_product2.pk)
        Listing.objects.get(pk=listing_for_product3.pk)

    def test_delete_view_deletes_only_listings_associated_to_the_product(self):
        """
        Test that other listings are not affected
        """
        product2 = ProductFactory(name="product 2", description="product 2")
        product2_listing = ListingFactory(title=product2.name, description=product2.description)
        ListingSetFactory(listing=product2_listing, product=product2, quantity=1)

        one_item_listing = ListingFactory(title=self.product.name, description=self.product.description)
        ListingSetFactory(listing=one_item_listing, product=self.product, quantity=1)

        product_listings_id = list(self.product.listings.values_list('id', flat=True))
        product2_listings_id = list(product2.listings.values_list('id', flat=True))

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check Product.DoesNotExist not thrown
        Product.objects.get(id=self.product.id)

        self.client.post(reverse('bazaar:product-delete', args=(self.product.pk, )))

        # Check product has been deleted
        self.assertRaises(Product.DoesNotExist, Product.objects.get, **{'id': self.product.id})

        # Check that all associated listings have been deleted
        self.assertEqual(len(Listing.objects.filter(id__in=product_listings_id)), 0)

        # Check that other listings are not affected
        self.assertNotEqual(len(product2.listings.all()), 0)
        self.assertEqual(len(Listing.objects.filter(id__in=product2_listings_id)),
                         len(product2_listings_id))

        self.assertEqual(len(Listing.objects.annotate(Count('products')).filter(products__count=0)), 0,
                         'There is at least one unassigned listing')
