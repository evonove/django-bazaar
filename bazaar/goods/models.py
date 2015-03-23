from __future__ import absolute_import
from __future__ import unicode_literals

from django.core.validators import MinValueValidator

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from .mixins import MoveableProductMixin
from .querysets import ProductsQuerySet
from bazaar.settings import bazaar_settings

from ..fields import MoneyField


@python_2_unicode_compatible
class Product(models.Model, MoveableProductMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ean = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=20, db_index=True, blank=True)
    photo = models.ImageField(upload_to='products', null=True, blank=True)
    price = MoneyField(help_text=_("Base default price for product"), validators=[MinValueValidator(limit_value=0)])

    product_type = models.IntegerField(choices=bazaar_settings.PRODUCT_TYPE_CHOICES, null=True, blank=True)

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


class CompositeProduct(Product, MoveableProductMixin):
    products = models.ManyToManyField("Product", related_name='composites', through='ProductSet')


class ProductSet(models.Model):
    composite = models.ForeignKey(CompositeProduct, related_name='product_sets')
    product = models.ForeignKey(Product, related_name='sets')
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('composite', 'product')

