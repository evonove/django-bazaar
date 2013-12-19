from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from moneyed import Money

from ..fields import MoneyField
from ..settings import bazaar_settings


class PriceListManager(models.Manager):
    use_for_related_fields = True

    def get_default(self):
        """
        Return the default price list instance
        """
        try:
            return self.get_query_set().get(pk=bazaar_settings.DEFAULT_PRICE_LIST_ID)
        except PriceList.DoesNotExist:
            raise ImproperlyConfigured("A default price list must exists. Please create one")


@python_2_unicode_compatible
class PriceList(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = PriceListManager()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    price_lists = models.ManyToManyField("PriceList", through="ProductPrice",
                                         related_name="products")

    class UnsavedException(Exception):
        pass

    @property
    def cost(self):
        """
        Defines the cost of the good
        """
        raise NotImplementedError

    @property
    def price(self):
        """
        The price for the product on the default price list
        """
        # Use .all() to allow access to prefetched queryset
        for product_price in self.prices.all():
            if product_price.price_list_id == bazaar_settings.DEFAULT_PRICE_LIST_ID:
                return product_price.price

        return Money(0, bazaar_settings.DEFAULT_CURRENCY)

    def set_price(self, price):
        """
        Sets the price for the product on the default price list
        """
        if not self.pk:
            raise self.UnsavedException("Save product before setting its price")

        price_list = PriceList.objects.get(id=bazaar_settings.DEFAULT_PRICE_LIST_ID)
        product_price, created = ProductPrice.objects.get_or_create(
            product=self, price_list=price_list)
        product_price.price = price
        product_price.save()

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
