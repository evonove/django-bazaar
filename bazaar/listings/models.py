from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from moneyed import Money
from bazaar.warehouse import api
from ..warehouse.api import get_storage_price, get_storage_quantity

from ..fields import MoneyField
from ..goods.models import Product
from ..settings import bazaar_settings

from .managers import ListingManager, PublishingManager


@python_2_unicode_compatible
class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    picture_url = models.URLField(blank=True)
    products = models.ManyToManyField(Product, related_name="listings", through="ListingSet")

    objects = ListingManager()

    class Meta:
        ordering = ["title"]

    @property
    def available_units(self):
        """
        Returns available units of the whole listing in the storage
        """
        availabilities = []
        min_available = 0
        for listing_set in self.listing_sets.all():
            product = listing_set.product
            quantity = listing_set.quantity
            if quantity and product:
                availabilities.append(api.get_storage_quantity(product) // quantity)
        if availabilities:
            min_available = min(availabilities)
        return min_available

    @property
    def cost(self):
        """
        Returns global cost for the listing
        """
        cost = Money(0, bazaar_settings.DEFAULT_CURRENCY)
        for ls in self.listing_sets.all():
            try:
                avg_cost = get_storage_price(ls.product)
            except models.ObjectDoesNotExist:
                avg_cost = 0

            cost += avg_cost * float(ls.quantity)

        return cost

    def is_unavailable(self):
        """
        Returns True when products stock cannot satisfy published listings
        """
        for ls in self.listing_sets.all():
            try:
                product_quantity = get_storage_quantity(ls.product)
            except models.ObjectDoesNotExist:
                product_quantity = 0

            if product_quantity < self.available_units * ls.quantity:
                return True
        return False

    def is_low_cost(self):

        listing_cost = self.cost
        for publishing in self.publishings.filter(status=Publishing.ACTIVE_PUBLISHING):
            if listing_cost > publishing.price:
                return True
        return False

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
    ACTIVE_PUBLISHING = 0
    COMPLETED_PUBLISHING = 1
    PUBLISHING_STATUS_CHOICES = (
        (ACTIVE_PUBLISHING, _("Active")),
        (COMPLETED_PUBLISHING, _("Completed")),
    )
    external_id = models.CharField(max_length=128, db_index=True)
    # Effective purchase cost, with purchase currency
    original_price = MoneyField()
    # Current selling price, with selling currency
    price = MoneyField()

    available_units = models.IntegerField(default=0)

    pub_date = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    status = models.IntegerField(choices=PUBLISHING_STATUS_CHOICES, default=ACTIVE_PUBLISHING)

    listing = models.ForeignKey(Listing, related_name="publishings")
    store = models.ForeignKey(Store, related_name="publishings")

    objects = PublishingManager()

    def get_template_name(self):
        return NotImplementedError("We doesn't provide a default publishing template.")

    def is_active(self):
        return self.status == self.ACTIVE_PUBLISHING

    def __str__(self):
        return "Publishing %s on %s" % (self.external_id, self.store)


@python_2_unicode_compatible
class Order(models.Model):
    ORDER_PENDING = 0
    ORDER_COMPLETED = 1
    ORDER_STATUS_CHOICES = (
        (ORDER_PENDING, _("Pending")),
        (ORDER_COMPLETED, _("Completed")),
    )
    external_id = models.CharField(max_length=256)
    store = models.ForeignKey(Store)
    publishing = models.ForeignKey(Publishing, null=True, blank=True)

    processed = models.BooleanField(default=False)
    bypass = models.BooleanField(default=False)

    quantity = models.IntegerField(default=1)

    status = models.IntegerField(max_length=50, choices=ORDER_STATUS_CHOICES, default=ORDER_PENDING)

    def __str__(self):
        return "Order %s from %s" % (self.external_id, self.store)


import django
if django.VERSION < (1, 7):
    from . import signals  # noqa
