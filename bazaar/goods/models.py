from __future__ import absolute_import
from __future__ import unicode_literals

from django.core.validators import MinValueValidator

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from bazaar.warehouse import api
from .mixins import MovableProductMixin, MovableCompositeProductMixin
from .querysets import ProductsQuerySet
from bazaar.settings import bazaar_settings

from ..fields import MoneyField


@python_2_unicode_compatible
class Product(MovableProductMixin, models.Model):
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


class CompositeProduct(MovableCompositeProductMixin, Product):
    products = models.ManyToManyField("Product", related_name='composites', through='ProductSet')


class ProductSet(models.Model):
    composite = models.ForeignKey(CompositeProduct, related_name='product_sets')
    product = models.ForeignKey(Product, related_name='sets')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('composite', 'product')


@receiver(post_save, sender=ProductSet)
def create_stock_and_set_price(sender, instance, *args, **kwargs):
    composite = instance.composite

    # FIXME: please, handle locations better than this
    # For me in the future: i'm sorry
    from ..warehouse.models import Stock, Location
    try:
        location = Location.objects.get(type=Location.LOCATION_STORAGE)
    except Location.MultipleObjectsReturned:
        location = Location.objects.filter(type=Location.LOCATION_STORAGE).first()
    except Location.DoesNotExist:
        location = Location.objects.create(type=Location.LOCATION_STORAGE)

    stock, created = Stock.objects.get_or_create(product=composite, location=location)
    if created:
        product_quantity = api.get_storage_quantity(instance.product)
        product_price = api.get_storage_price(instance.product)
        composite_quantity = product_quantity // instance.quantity
        composite_price = product_price * instance.quantity
        stock.quantity = composite_quantity
        stock.unit_price = composite_price
        stock.save()
    else:
        quantities = []
        unit_price = 0
        for ps in composite.product_sets.all():
            product_quantity = api.get_storage_quantity(ps.product)
            product_price = api.get_storage_price(ps.product)
            quantities.append(product_quantity // ps.quantity)
            unit_price = unit_price + (product_price.amount * ps.quantity)
        if stock.unit_price != unit_price:
            stock.unit_price = unit_price
        if min(quantities) != api.get_storage_quantity(composite):
            stock.quantity = min(quantities)
        stock.save()
