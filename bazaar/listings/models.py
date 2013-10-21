from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from ..fields import MoneyField
from ..goods.models import Product


@python_2_unicode_compatible
class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    sales_units = models.IntegerField(default=1)

    # TODO: this should become a gallery
    image = models.ImageField(upload_to="listing_images")
    product = models.ManyToManyField(Product, related_name="listings")

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Store(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Publishing(models.Model):
    external_id = models.CharField(max_length=128)

    price = MoneyField()

    available_units = models.IntegerField()
    published = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=timezone.now)

    listing = models.ForeignKey(Listing, related_name="publishings")
    store = models.ForeignKey(Store, related_name="publishings")

    def __str__(self):
        return "Publishing %s on %s" % (self.external_id, self.store)
