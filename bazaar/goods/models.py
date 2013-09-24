from __future__ import unicode_literals

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# TODO: this dependency should be optional, maybe based on INSTALLED APPS
from bazaar.warehouse.models import Stock, Movement


@python_2_unicode_compatible
class AbstractGood(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    elements = generic.GenericRelation("ProductElement")

    stocks = generic.GenericRelation(Stock)
    movements = generic.GenericRelation(Movement)

    class Meta:
        abstract = True

    @property
    def cost(self):
        """
        Defines the cost of the good
        """
        raise NotImplementedError

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PriceList(models.Model):
    name = models.CharField(max_length=100, unique=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price_lists = models.ManyToManyField("PriceList", through="ProductPrice", related_name="products")

    @property
    def price(self):
        """
        The price for the product on the default price list
        """
        try:
            product_price = self.prices.get(price_list__default=True)
            return product_price.price
        except ProductPrice.DoesNotExist:
            return None

    @property
    def cost(self):
        """
        The cost of the product as the sum of the costs of its goods
        """
        cost = 0.0
        for element in self.elements:
            cost += element.good.cost

        return cost

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
class ProductPrice(models.Model):
    product = models.ForeignKey(Product, related_name="prices")
    price_list = models.ForeignKey(PriceList)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return ""
