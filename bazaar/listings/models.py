from __future__ import unicode_literals

import django

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager

from bazaar.listings.managers import PublishingsManager
from bazaar.listings.querysets import PublishingsQuerySet
from bazaar.warehouse import api

from ..fields import MoneyField, SKUField, create_sku
from ..goods.models import Product
from ..settings import bazaar_settings

from .managers import ListingManager


@python_2_unicode_compatible
class Listing(models.Model):

    # DELETE in future
    # products = models.ManyToManyField(Product, related_name="listings_old", through="ListingSet")
    # title = models.CharField(max_length=100)
    # picture_url = models.URLField(blank=True)
    # description = models.TextField(blank=True)
    # END of delete section

    product = models.ForeignKey(Product, related_name="listings", null=True)
    sku = SKUField(default=create_sku)

    objects = ListingManager()

    class Meta:
        ordering = ["product__name"]

    @property
    def _title(self):
        """
        Returns product's name
        """
        if self.product:
            return self.product.name
        return 'No product'

    @property
    def _description(self):
        """
        Returns product's description
        """
        if self.product:
            return self.product.description
        return 'No product'

    @property
    def _picture_url(self):
        """
        Returns product picture's url
        """
        if self.product:
            if hasattr(self.product, 'photo') and hasattr(self.product.photo, 'url'):
                return self.product.photo.url
        return ''

    @property
    def available_units(self):
        """
        Returns available units of the whole listing in the storage
        """
        return api.get_storage_quantity(self.product)

    @property
    def cost(self):
        """
        Returns global cost for the listing
        """
        return api.get_storage_price(self.product)

    def is_unavailable(self):
        """
        Returns True when products stock cannot satisfy published listings
        """
        try:
            product_quantity = api.get_storage_quantity(self.product)
        except models.ObjectDoesNotExist:
            product_quantity = 0
        for publishing in self.publishings.all():
            if publishing.is_active():
                if product_quantity < publishing.available_units:
                    return True
        return False

    def is_highly_available(self):
        """
        Return True when products stock has more elements than published one
        """
        try:
            product_quantity = api.get_storage_quantity(self.product)
        except models.ObjectDoesNotExist:
            product_quantity = 0
        for publishing in self.publishings.all():
            if publishing.is_active():
                if product_quantity - publishing.available_units > 2:
                        return True
        return False

    def is_low_cost(self):

        listing_cost = self.cost
        for publishing in self.publishings.filter(status=Publishing.ACTIVE_PUBLISHING):
            if listing_cost > publishing.price:
                return True
        return False

    def __str__(self):
        name = ''
        has_product_name = hasattr(self.product, 'name')
        if has_product_name:
            name = self.product.name
        return ' '.join(filter(None, (name, '({})'.format(self.sku))))


@receiver(post_save, sender=Product)
def create_listing_for_product(sender, instance, **kwargs):
    if not bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION:
        return

    if not kwargs['created']:
        return

    if hasattr(instance, 'compositeproduct'):
        return

    # TODO: Is needed here?
    from bazaar.goods.api import listing_bulk_creation
    listing_bulk_creation(Product.objects.filter(pk=instance.id).all())


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
    title = models.CharField(max_length=256, blank=True, null=True)

    # TODO: Here we keep both picture_url and photo for compatibility, but picture_url will have to be removed
    picture_url = models.URLField(null=True, blank=True)
    photo = models.ImageField(upload_to='publishings', null=True, blank=True)

    description = models.TextField(blank=True, null=True)

    # Effective purchase cost, with purchase currency
    original_price = MoneyField()

    # Current selling price, with selling currency
    price = MoneyField()

    available_units = models.IntegerField(default=0)

    pub_date = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    status = models.IntegerField(choices=PUBLISHING_STATUS_CHOICES, default=ACTIVE_PUBLISHING)

    listing = models.ForeignKey(Listing, related_name="publishings", null=True, blank=False)
    store = models.ForeignKey(Store, related_name="publishings")

    objects = PublishingsManager.from_queryset(PublishingsQuerySet)()

    def get_template_name(self):
        return NotImplementedError("We doesn't provide a default publishing template.")

    def is_active(self):
        return self.status == self.ACTIVE_PUBLISHING

    def __str__(self):
        return "Publishing %s on %s" % (self.external_id, self.store)

    class Meta:
        unique_together = ("external_id", "store")


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

    objects = InheritanceManager()

    def __str__(self):
        return "Order %s from %s" % (self.external_id, self.store)

    class Meta:
        unique_together = ("external_id", "store")


if django.VERSION < (1, 7):
    from . import signals  # noqa
