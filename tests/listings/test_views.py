from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.forms import forms
from django.test import TestCase

from django.utils.translation import ugettext as _
from bazaar.listings.models import Listing

from rest_framework import status
from tests import factories as f
from tests.factories import PublishingFactory, ListingFactory, ListingSetFactory


class TestBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', email='test@test.it', password='test')


class TestListingsListView(TestBase):
    def test_list_view(self):
        """
        Test that list view works fine
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:listings-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        listings = response.context_data['listing_list']
        self.assertEqual(listings.count(), 1)
        self.assertEqual(listings[0].title, self.listing.title)
        self.assertEqual(listings[0].description, self.listing.description)
        self.assertEqual(listings[0].picture_url, self.listing.picture_url)
        self.assertEqual(listings[0].sku, self.listing.sku)

    def test_list_view_not_working_without_login(self):
        """
        Test that trying to call the list view without being logged redirects to the login page
        """
        response = self.client.get(reverse('bazaar:listings-list'))
        self.assertRedirects(response, '/accounts/login/?next=/listings/')

    def test_list_view_no_products(self):
        """
        Test that a void list view displays "no products"
        """
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:listings-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        listings = response.context_data['listing_list']

        self.assertEqual(listings.count(), 0)
        self.assertIn(_('There are 0 listings').encode(encoding='UTF-8'), response.content)


class TestListingUpdateView(TestBase):
    def test_update_view_not_working_without_login(self):
        """
        Test that the update view redirects to the login page if the user is not logged
        """
        response = self.client.get(reverse('bazaar:listings-update', kwargs={'pk': 1}))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('bazaar:listings-update', kwargs={'pk': 1}))

    def test_update_simple_list_view(self):
        """
        Test that the update view works fine
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing

        one_item_listing = ListingFactory(title=self.product.name, description=self.product.description)
        ListingSetFactory(listing=one_item_listing, product=self.product, quantity=1)

        self.client.login(username=self.user.username, password='test')
        data = {
            'title': 'ModifiedTitle',
            'picture_url': 'http://myurl.com/myinage.jpg',
            'description': 'Description of ModifiedTitle',
            'quantity': 2,
            'product': self.product.id,
        }
        response = self.client.post(reverse('bazaar:listings-update', kwargs={'pk': self.product.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        listing = Listing.objects.get(products__id=self.product.pk, title='ModifiedTitle')
        self.assertEqual(listing.title, 'ModifiedTitle')

    def test_update_view_fails_with_incorrect_data(self):
        """
        Test that the update view fails with incorrect input [quantity is not a number, product is None]
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing

        one_item_listing = ListingFactory(title=self.product.name, description=self.product.description)
        ListingSetFactory(listing=one_item_listing, product=self.product, quantity=1)

        self.client.login(username=self.user.username, password='test')
        data = {
            'title': 'ModifiedTitle',
            'picture_url': 'http://myurl.com/myinage.jpg',
            'description': 'Description of ModifiedTitle',
            'quantity': 'two'
        }
        response = self.client.post(reverse('bazaar:listings-update',
                                            kwargs={'pk': self.product.listing_sets.all()[0].pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        listing_exits = Listing.objects.filter(products__id=self.product.pk, title='ModifiedTitle').exists()
        self.assertEqual(listing_exits, False)

    def test_update_simple_view_fails_when_listingset_attrs_are_changed_in_a_listing_with_associated_publishing(self):
        """
        Test that the update view fails with incorrect input [quantity is not a number, product is None]
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing
        ListingSetFactory(listing=self.listing, product=self.product, quantity=2)

        self.client.login(username=self.user.username, password='test')
        data = {
            'title': 'ModifiedTitle',
            'picture_url': 'http://myurl.com/myinage.jpg',
            'description': 'Description of ModifiedTitle',
            'quantity': 1,
            'product': self.product.id,
        }
        response = self.client.post(reverse('bazaar:listings-update',
                                            kwargs={'pk': self.product.listing_sets.all()[0].pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('one listingset per listing', response.context_data['form'].errors[forms.NON_FIELD_ERRORS][0])

    def test_update_simple_view_fails_when_there_are_mone_listingset_associated_to_listing(self):
        """
        Test that the update view fails with incorrect input [quantity is not a number, product is None]
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing
        PublishingFactory(listing=self.listing)

        self.client.login(username=self.user.username, password='test')
        data = {
            'title': 'ModifiedTitle',
            'picture_url': 'http://myurl.com/myinage.jpg',
            'description': 'Description of ModifiedTitle',
            'quantity': 2,
            'product': self.product.id,
        }
        response = self.client.post(reverse('bazaar:listings-update',
                                            kwargs={'pk': self.product.listing_sets.all()[0].pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Updating listingset is denied', response.context_data['form'].errors[forms.NON_FIELD_ERRORS][0])


class TestListingCreateView(TestBase):
    def test_create_simple_listing_view(self):
        """
        Test that the create view works fine
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing

        self.client.login(username=self.user.username, password='test')
        data = {
            'title': 'ModifiedTitle',
            'picture_url': 'http://myurl.com/myinage.jpg',
            'description': 'Description of ModifiedTitle',
            'quantity': '2',
            'product': self.product.id
        }
        response = self.client.post(reverse('bazaar:listings-create'), data=data)
        new_listing = Listing.objects.get(products__id=self.product.pk, title='ModifiedTitle')
        self.assertRedirects(response, '/listings/%s/' % new_listing.pk)

    def test_create_view_not_working_without_login(self):
        """
        Test that the create view redirects to the login page if the user is not logged
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing
        data = {
            'title': 'ModifiedTitle',
            'picture_url': 'http://myurl.com/myinage.jpg',
            'description': 'Description of ModifiedTitle',
            'quantity': 2,
            'product': self.product.id
        }
        response = self.client.post(reverse('bazaar:listings-create'), data=data)
        self.assertRedirects(response, '/accounts/login/?next=/listings/new/')

    def test_create_view_not_working_with_a_not_numeric_quantity(self):
        """
        Test that the create view doesn't work with negative price
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing
        self.client.login(username=self.user.username, password='test')
        data = {
            'title': 'ModifiedTitle',
            'picture_url': 'http://myurl.com/myinage.jpg',
            'description': 'Description of ModifiedTitle',
            'quantity': 'two',
            'product': self.product.id
        }
        response = self.client.post(reverse('bazaar:listings-create'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Listing.objects.filter(products__id=self.product.pk, title='ModifiedTitle').count(), 0)


class TestDeleteView(TestBase):
    def test_delete_view_not_working_without_login(self):
        """
        Test that the delete view redirects to the login page if the user is not logged
        """
        response = self.client.get(reverse('bazaar:listings-delete', kwargs={'pk': 1}))
        self.assertRedirects(response, '/accounts/login/?next=/listings/delete/%s/' % 1)

    def test_delete_view(self):
        """
        Test that the delete view works fine
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(reverse('bazaar:listings-delete', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        listing_exists = Listing.objects.filter(pk=self.listing.pk).exists()
        self.assertEqual(listing_exists, False)

    def test_delete_view_let_delete_a_listing_only_if_it_has_not_publishing_associated(self):
        """
        Test that the product has associated publishings
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listing_sets.all()[0].listing
        publishing = PublishingFactory(listing=self.listing)

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(reverse('bazaar:listings-delete', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        publishing.delete()

        response = self.client.post(reverse('bazaar:listings-delete', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        listing_exists = Listing.objects.filter(pk=self.listing.pk).exists()
        self.assertEqual(listing_exists, False)