from __future__ import absolute_import
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone

from bazaar.listings.filters import LowPriceListingFilter, UnavailableListingFilter, HighAvailabilityListingFilter, \
    AvailableUnitsFilter
from bazaar.listings.models import Listing, Order

from .. import factories as f


class TestListingManager(TestCase):
    def setUp(self):
        self.storage = f.StorageFactory()
        self.lost_and_found = f.LostFoundFactory()
        self.output = f.OutputFactory()

        self.product_1 = f.ProductFactory()
        self.listing_1 = self.product_1.listings.first()
        self.publishing_1 = f.PublishingFactory(price=1, listing=self.listing_1, available_units=1)

        self.product_2 = f.ProductFactory()
        self.listing_2 = self.product_2.listings.first()
        self.publishing_2 = f.PublishingFactory(price=1, listing=self.listing_2, available_units=4)

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
        self.product_2.move(from_location=self.lost_and_found, to_location=self.storage, price_multiplier=0.2)

        filter = LowPriceListingFilter()
        listings = filter.filter(Listing.objects.all(), True)

        self.assertEqual(listings.count(), 1)
        self.assertEqual(listings.first(), self.listing_1)


class TestPublishingManager(TestCase):
    def setUp(self):
        pass

    def test_main_publishings(self):
        pass


class TestOrderManager(TestCase):
    def test_last_modified_empty_queryset(self):
        """
        If we don't have any order, simply return an empty QuerySet
        """
        order = Order.objects.last_modified()
        self.assertEqual(order.count(), 0)

    def test_last_modified_empty_item(self):
        """
        If we have an Order but it hasn't the modified value, we should ensure
        that an empty QuerySet is returned.
        """
        # test case with an Order without modified value
        f.OrderFactory(modified=None)
        # we should have an empty QuerySet
        order = Order.objects.last_modified()
        self.assertEqual(order.count(), 0)

    def test_last_modified_single_item(self):
        """
        The only available Order has all dates as 2016-1-1.
        If we call the last_modified() we should retrieve this Order with
        the correct modified date.
        """
        # test case
        date = timezone.datetime(2016, 1, 1, tzinfo=timezone.utc)
        f.OrderFactory(paid_time=date, modified=date, shipped_time=date)
        # grab the last modified order
        order = Order.objects.last_modified()
        self.assertEqual(order.count(), 1)
        self.assertEqual(order.first().modified, date)

    def test_last_modified_multiple_item(self):
        """
        We have multiple Orders:
            - 2 with old dates for all fields
            - 1 with old dates for all fields except modified
        Through last_modified(), we should retrieve the last modified order, ensuring
        that the returned value is a QuerySet with just one item.
        """
        # test case
        date_old = timezone.datetime(2016, 1, 1, tzinfo=timezone.utc)
        date_new = timezone.datetime(2016, 1, 2, tzinfo=timezone.utc)
        f.OrderFactory(paid_time=date_old, modified=date_old, shipped_time=date_old)
        f.OrderFactory(paid_time=date_old, modified=date_old, shipped_time=date_old)
        expected = f.OrderFactory(paid_time=date_old, modified=date_new, shipped_time=date_old)
        # the last modified order should match the last one because
        # its modified date is the most recent
        order = Order.objects.last_modified()
        self.assertEqual(order.count(), 1)
        self.assertEqual(order.first(), expected)
