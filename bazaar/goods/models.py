from __future__ import unicode_literals

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class AbstractGood(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price_lists = models.ManyToManyField("PriceList", through="ProductPrice", related_name="products")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductElement(models.Model):
    product = models.ForeignKey(Product, related_name="elements")
    quantity = models.IntegerField(default=1)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    good = generic.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return ""


@python_2_unicode_compatible
class PriceList(models.Model):
    name = models.CharField(max_length=100, unique=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductPrice(models.Model):
    product = models.ForeignKey(Product)
    price_list = models.ForeignKey(PriceList)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return ""
