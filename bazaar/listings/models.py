from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ..fields import MoneyField
from ..goods.models import Product


class ListingManager(models.Manager):
    def low_stock_ids(self):
        """
        Returns a list of ids of the listings for which the quantity of a product in stock
        is less than the amount needed to satisfy it
        """
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("""SELECT DISTINCT l.id
            FROM listings_listing AS l join listings_listingset AS ls
            ON l.id = ls.listing_id JOIN goods_product AS p
            ON p.id = ls.product_id JOIN listings_publishing AS pu
            ON pu.listing_id = l.id LEFT JOIN warehouse_stock AS s
            ON p.id = s.product_id
            WHERE COALESCE(s.quantity, 0) <= (
                SELECT SUM(p1.available_units * ls.quantity)
                FROM listings_publishing AS p1
                WHERE p1.listing_id = l.id)
            GROUP BY l.id, p.id""")

        res = cursor.fetchall()
        return [r[0] for r in res]


@python_2_unicode_compatible
class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    picture_url = models.URLField(blank=True)
    products = models.ManyToManyField(Product, related_name="listings", through="ListingSet")

    objects = ListingManager()

    @property
    def available_units(self):
        """
        Returns available units across all publishings
        """
        available = 0
        for publishing in self.publishings.all():
            available += publishing.available_units

        return available

    def is_stock_low(self):
        """
        Returns True when products stock cannot satisfy published listings
        """
        for ls in self.listing_sets.all():
            try:
                product_quantity = ls.product.stock.quantity
            except models.ObjectDoesNotExist:
                product_quantity = 0

            if product_quantity < self.available_units * ls.quantity:
                return True

    def __str__(self):
        return self.title


class ListingSet(models.Model):
    quantity = models.DecimalField(max_digits=30, decimal_places=4, default=1)

    product = models.ForeignKey(Product, related_name="listing_sets")
    listing = models.ForeignKey(Listing, related_name="listing_sets")


@python_2_unicode_compatible
class Store(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Publishing(models.Model):
    external_id = models.CharField(max_length=128)

    price = MoneyField()

    available_units = models.IntegerField(default=0)

    pub_date = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    listing = models.ForeignKey(Listing, related_name="publishings")
    store = models.ForeignKey(Store, related_name="publishings")

    def __str__(self):
        return "Publishing %s on %s" % (self.external_id, self.store)
