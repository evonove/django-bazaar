from __future__ import absolute_import
from __future__ import unicode_literals
from django.conf import settings
from django.core.validators import MinValueValidator

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from bazaar.goods.querysets import ProductsQuerySet

from ..fields import MoneyField


@python_2_unicode_compatible
class PriceList(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ean = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=20, db_index=True, blank=True)
    photo = models.ImageField(upload_to='products', null=True, blank=True)
    price = MoneyField(help_text=_("Base default price for product"), validators=[MinValueValidator(limit_value=0)])
    price_lists = models.ManyToManyField("PriceList", through="ProductPrice",
                                         related_name="products")
    product_type = models.IntegerField(choices=settings.PRODUCT_TYPE_CHOICES, null=True)


    objects = ProductsQuerySet.as_manager()

    @property
    def cost(self):
        """
        Defines the cost of the good
        """
        from ..warehouse.api import get_storage_price
        return get_storage_price(self)

    @property
    def quantity(self):
        from ..warehouse.api import get_storage_quantity
        return get_storage_quantity(self)

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
