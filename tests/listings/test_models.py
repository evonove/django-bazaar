#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

import datetime
import pytz

from bazaar.listings.models import Store, Listing, Publishing
from moneyed import Money
from ..factories import (ProductFactory, StockFactory, ListingFactory, PublishingFactory)


class TestPublishingModelManager(TestCase):
    def setUp(self):
        self.date1 = datetime.datetime(2010, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.date2 = datetime.datetime(2011, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.date3 = datetime.datetime(2012, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.date4 = datetime.datetime(2013, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.listing_a = Listing.objects.create()
        self.big_store = Store.objects.create(slug="big", name="big_store")
        self.small_store = Store.objects.create(slug="small", name="small_store")

    def tearDown(self):
        Listing.objects.all().delete()
        Store.objects.all().delete()
        Publishing.objects.all().delete()

    def test_publishing_manager_get_all_actives(self):
        publishing1 = Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date1,
                                                last_modified=self.date1, listing=self.listing_a,
                                                store=self.small_store, external_id='1')
        publishing2 = Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date2,
                                                last_modified=self.date2, listing=self.listing_a,
                                                store=self.small_store, external_id='2')
        publishing3 = Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date3,
                                                last_modified=self.date3, listing=self.listing_a,
                                                store=self.small_store, external_id='3')
        publishing4 = Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date4,
                                                last_modified=self.date4, listing=self.listing_a,
                                                store=self.big_store, external_id='4')

        self.assertEqual(publishing1.store.slug, "small")
        self.assertEqual(publishing2.store.slug, "small")
        self.assertEqual(publishing3.store.slug, "small")
        self.assertEqual(publishing4.store.slug, "big")

        active_pubs = Publishing.objects.main_publishings(self.listing_a)
        self.assertEqual(len(active_pubs), 3)

    def test_publishing_manager_get_only_last_completed_same_store(self):
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date1, last_modified=self.date1,
                                  listing=self.listing_a, store=self.small_store, external_id='1')
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date2, last_modified=self.date2,
                                  listing=self.listing_a, store=self.small_store, external_id='2')
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date3, last_modified=self.date3,
                                  listing=self.listing_a, store=self.small_store, external_id='3')

        completed_pubs = Publishing.objects.main_publishings(self.listing_a)
        self.assertEqual(len(completed_pubs), 1)
        self.assertEqual(completed_pubs[0].pub_date, self.date3)

    def test_publishing_manager_all_features(self):
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date1, last_modified=self.date1,
                                  listing=self.listing_a, store=self.small_store, external_id='1')
        Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date2, last_modified=self.date2,
                                  listing=self.listing_a, store=self.small_store, external_id='2')
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date3, last_modified=self.date3,
                                  listing=self.listing_a, store=self.small_store, external_id='3')
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date4, last_modified=self.date4,
                                  listing=self.listing_a, store=self.big_store, external_id='4')

        pubs = Publishing.objects.main_publishings(self.listing_a)
        self.assertEqual(len(pubs), 2)
        act_pub = pubs[0]
        comp_pub = pubs[1]

        if act_pub.status == Publishing.COMPLETED_PUBLISHING:
            change = act_pub
            act_pub = comp_pub
            comp_pub = change
        self.assertEqual(act_pub.status, Publishing.ACTIVE_PUBLISHING)
        self.assertEqual(comp_pub.status, Publishing.COMPLETED_PUBLISHING)


class TestListingModel(TestCase):
    def setUp(self):
        self.product = ProductFactory()
        self.listing = ListingFactory(product=self.product)
        self.stock_a = StockFactory(product=self.product, unit_price=2.0, quantity=30)

    def test_retrieve_cost_attribute(self):
        self.assertEqual(self.listing.cost, Money(2, 'EUR'))

    def test_sku_field_created_on_listing_creation(self):
        self.assertTrue(self.listing.sku)

    def test_sku_field_not_updated_on_save(self):
        listing = ListingFactory()
        sku = listing.sku

        listing.save()

        listing = Listing.objects.get(pk=listing.pk)
        self.assertEqual(sku, listing.sku)

    def test_listing_unavailable(self):
        PublishingFactory(listing=self.listing, available_units=35)
        self.assertTrue(self.listing.is_unavailable())

    def test_listing_is_highly_available(self):
        PublishingFactory(listing=self.listing, available_units=25)
        self.assertTrue(self.listing.is_highly_available())

    def test_is_low_cost(self):
        PublishingFactory(listing=self.listing, available_units=25, price=1)
        self.assertTrue(self.listing.is_low_cost())
