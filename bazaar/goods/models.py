from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Good(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    goods = models.ManyToManyField(Good, through="ProductGood", related_name="products")
    price_lists = models.ManyToManyField("PriceList", through="ProductPrice", related_name="products")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductGood(models.Model):
    product = models.ForeignKey(Product)
    good = models.ForeignKey(Good)
    quantity = models.IntegerField(default=1)


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
