from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ..fields import MoneyField
from ..warehouse.api import get_storage_price


@python_2_unicode_compatible
class PriceList(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    price = MoneyField(help_text=_("Base default price for product"))

    price_lists = models.ManyToManyField("PriceList", through="ProductPrice",
                                         related_name="products")

    @property
    def cost(self):
        """
        Defines the cost of the good
        """
        return get_storage_price(self)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductPrice(models.Model):
    price = MoneyField()

    product = models.ForeignKey(Product, related_name="prices")
    price_list = models.ForeignKey(PriceList, related_name="prices")

    class Meta:
        unique_together = ('product', 'price_list')

    def __str__(self):
        return "'%s' %s %s" % (self.product, self.price_list, self.price)
