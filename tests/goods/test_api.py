from __future__ import unicode_literals

from bazaar.goods.api import listing_bulk_creation
from bazaar.goods.models import Product
from bazaar.listings.models import Listing
from bazaar.settings import bazaar_settings

from ..base import BaseTestCase
from ..factories import ProductFactory, ListingFactory, ListingSetFactory


class TestApi(BaseTestCase):

    def test_listing_bulk_creation_with_product_that_already_have_a_listing(self):
        """
        Test that the method does not create any extra 1xlisting, since the products
        that are passed as parameters already have an associated 1xlisting
        """

        # turn on automatic listing creation on product creation
        old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = True

        # create 3 products with 1xlisting
        ProductFactory()
        ProductFactory()
        ProductFactory()

        self.assertEqual(Listing.objects.all().count(), 3)
        listing_bulk_creation(Product.objects.all())
        self.assertEqual(Listing.objects.all().count(), 3)

        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = old_setting_value

    def test_listing_bulk_creation_with_product_that_has_no_listing(self):
        """
        Test that the method does create a 1xlisting for every product passed in
        """

        # turn off automatic listing creation on product creation
        old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = False

        # create product with no associated 1xlisting
        product = ProductFactory()

        self.assertEqual(Listing.objects.all().count(), 0)

        listing_bulk_creation(Product.objects.all())

        self.assertEqual(Listing.objects.all().count(), 1)
        self.assertEqual(Listing.objects.all()[0].listing_sets.all()[0].product, product)

        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = old_setting_value

    def test_listing_bulk_creation_correctly_checks_listings(self):
        """
        There may be some listing with more than one product with quantity 1.
        Test that the method listing_bulk_creation doesn't consider these listings
        as 1xlistings
        """

        # turn off automatic listing creation on product creation
        old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = False

        self.assertEqual(Listing.objects.all().count(), 0)

        # create a listing with 2 products
        listing = ListingFactory()
        ListingSetFactory(product=ProductFactory(), listing=listing)
        ListingSetFactory(product=ProductFactory(), listing=listing)

        self.assertEqual(Listing.objects.all().count(), 1)

        listing_bulk_creation(Product.objects.all())

        self.assertEqual(Listing.objects.all().count(), 3)

        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = old_setting_value
