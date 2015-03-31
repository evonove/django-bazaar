from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from django.utils.translation import ugettext as _
from bazaar.listings.models import Listing

from rest_framework import status
from tests import factories as f
from tests.factories import PublishingFactory, ListingFactory


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
        self.listing = self.product.listings.first()

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

    def test_update_listing_does_not_change_sku(self):
        self.client.login(username=self.user.username, password='test')

        product = f.ProductFactory()
        listing = product.listings.first()

        self.client.login(username=self.user.username, password='test')
        data = {'product': product.pk}
        response = self.client.post(reverse('bazaar:listings-update', kwargs={'pk': listing.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        modified_listing = Listing.objects.get(pk=listing.pk)
        self.assertEqual(listing.sku, modified_listing.sku)

    def test_new_simple_view_has_back_button(self):
        """
        Test that the new view has back and save button
        """

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(reverse('bazaar:listings-create'))
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('href="/listings/"', content)
        self.assertIn('id="submit-id-save"', content)


class TestListingCreateView(TestBase):
    def test_create_simple_listing_view(self):
        """
        Test that the create view works fine
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listings.first()

        self.client.login(username=self.user.username, password='test')
        data = {'product': self.product.id}
        response = self.client.post(reverse('bazaar:listings-create'), data=data)
        new_listing = Listing.objects.exclude(sku=self.listing.sku).first()
        self.assertRedirects(response, '/listings/%s/' % new_listing.pk)

    def test_create_view_not_working_without_login(self):
        """
        Test that the create view redirects to the login page if the user is not logged
        """
        # By default this operation will create a bound listing x1 of that product
        self.product = f.ProductFactory(name='product1', price=2, description='the best you can have!')
        self.listing = self.product.listings.first()
        data = {'product': self.product.id}
        response = self.client.post(reverse('bazaar:listings-create'), data=data)
        self.assertRedirects(response, '/accounts/login/?next=/listings/new/')


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
        self.listing = self.product.listings.first()

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
        self.listing = self.product.listings.first()
        publishing = PublishingFactory(listing=self.listing)

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(reverse('bazaar:listings-delete', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        publishing.delete()

        response = self.client.post(reverse('bazaar:listings-delete', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        listing_exists = Listing.objects.filter(pk=self.listing.pk).exists()
        self.assertEqual(listing_exists, False)
