#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

import datetime
import pytz

from bazaar.listings.models import Store, Listing, Publishing
from moneyed import Money
from ..factories import (ProductFactory, StockFactory, ListingFactory, ListingSetFactory)


class TestPublishingModelManager(TestCase):
    def setUp(self):
        self.date1 = datetime.datetime(2010, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.date2 = datetime.datetime(2011, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.date3 = datetime.datetime(2012, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.date4 = datetime.datetime(2013, 1, 1, 0, 0, tzinfo=pytz.UTC)
        self.listing_a = Listing.objects.create(title="listing_a")
        self.big_store = Store.objects.create(slug="big", name="big_store")
        self.small_store = Store.objects.create(slug="small", name="small_store")

    def tearDown(self):
        Listing.objects.all().delete()
        Store.objects.all().delete()
        Publishing.objects.all().delete()

    def test_publishing_manager_get_all_actives(self):
        publishing1 = Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date1,
                                                last_modified=self.date1, listing=self.listing_a,
                                                store=self.small_store)
        publishing2 = Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date2,
                                                last_modified=self.date2, listing=self.listing_a,
                                                store=self.small_store)
        publishing3 = Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date3,
                                                last_modified=self.date3, listing=self.listing_a,
                                                store=self.small_store)
        publishing4 = Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date4,
                                                last_modified=self.date4, listing=self.listing_a,
                                                store=self.big_store)

        self.assertEqual(publishing1.store.slug, "small")
        self.assertEqual(publishing2.store.slug, "small")
        self.assertEqual(publishing3.store.slug, "small")
        self.assertEqual(publishing4.store.slug, "big")

        active_pubs = Publishing.objects.main_publishings(self.listing_a)
        self.assertEqual(len(active_pubs), 3)

    def test_publishing_manager_get_only_last_completed_same_store(self):
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date1, last_modified=self.date1,
                                  listing=self.listing_a, store=self.small_store)
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date2, last_modified=self.date2,
                                  listing=self.listing_a, store=self.small_store)
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date3, last_modified=self.date3,
                                  listing=self.listing_a, store=self.small_store)

        completed_pubs = Publishing.objects.main_publishings(self.listing_a)
        self.assertEqual(len(completed_pubs), 1)
        self.assertEqual(completed_pubs[0].pub_date, self.date3)

    def test_publishing_manager_all_features(self):
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date1, last_modified=self.date1,
                                  listing=self.listing_a, store=self.small_store)
        Publishing.objects.create(status=Publishing.ACTIVE_PUBLISHING, pub_date=self.date2, last_modified=self.date2,
                                  listing=self.listing_a, store=self.small_store)
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date3, last_modified=self.date3,
                                  listing=self.listing_a, store=self.small_store)
        Publishing.objects.create(status=Publishing.COMPLETED_PUBLISHING, pub_date=self.date4, last_modified=self.date4,
                                  listing=self.listing_a, store=self.big_store)

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
        self.listing = ListingFactory()
        self.stock_a = StockFactory(product=self.product, unit_price=2.0, quantity=30)
        self.listing_set = ListingSetFactory(product=self.product, listing=self.listing)

    def tearDown(self):
        pass

    def test_retrieve_cost_attribute(self):
        self.assertEqual(self.listing.cost, Money(2, 'EUR'))

    def test_sku_field_created_on_listing_creation(self):
        self.assertTrue(self.listing.sku)
