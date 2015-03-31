from __future__ import absolute_import
from __future__ import unicode_literals

from django.test import TestCase
from .. import factories as f
from bazaar.listings.filters import LowPriceListingFilter, UnavailableListingFilter, HighAvailabilityListingFilter, \
    AvailableUnitsFilter
from bazaar.listings.models import Listing


class TestListingManager(TestCase):
    def setUp(self):
        self.storage = f.StorageFactory()
        self.lost_and_found = f.LostFoundFactory()
        self.output = f.OutputFactory()

        self.product_1 = f.ProductFactory()
        self.listing_1 = f.ListingFactory(product=self.product_1)
        self.publishing_1 = f.PublishingFactory(listing=self.listing_1, available_units=1)

        self.product_2 = f.ProductFactory()
        self.listing_2 = f.ListingFactory(product=self.product_2)
        self.publishing_2 = f.PublishingFactory(listing=self.listing_2, available_units=4)

    def test_high_availability(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=4)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, quantity=2)

        highly_available_filter = HighAvailabilityListingFilter()
        listings = highly_available_filter.filter(Listing.objects.all(), True)

        self.assertEqual(listings.count(), 1)
        self.assertEqual(listings.first(), self.listing_1)

    def test_available_units(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=1)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, quantity=2)

        available_filter = AvailableUnitsFilter(value=2)
        listings = available_filter.filter(Listing.objects.all(), True)

        self.assertEqual(listings.count(), 1)
        self.assertEqual(listings.first(), self.listing_1)

    def test_low_availability(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, quantity=1)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, quantity=2)

        unavailable_filter = UnavailableListingFilter()
        listings = unavailable_filter.filter(Listing.objects.all(), True)

        self.assertEqual(listings.count(), 1)
        self.assertEqual(listings.first(), self.listing_2)

    def test_low_cost(self):
        self.product_1.move(from_location=self.lost_and_found, to_location=self.storage, price_multiplier=2)
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, price_multiplier=0.1)

        filter = LowPriceListingFilter()
        listings = filter.filter(Listing.objects.all(), True)

        self.assertEqual(listings.count(), 1)
        self.assertEqual(listings.first(), self.listing_1)


class TestPublishingManager(TestCase):
    def setUp(self):
        pass

    def test_main_publishings(self):
        pass