from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from bazaar.goods.models import Good


@python_2_unicode_compatible
class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    goods = models.ManyToManyField(Good, through="Stock")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Stock(models.Model):
    quantity = models.IntegerField(default=0)

    warehouse = models.ForeignKey(Warehouse)
    good = models.ForeignKey(Good)

    def __str__(self):
        return _("Stock for %s in warehouse %s %s: real %d - expected %d") % (
            self.good, self.warehouse, self.real_stock, self.expected_stock)


@python_2_unicode_compatible
class Movement(models.Model):
    price_in = models.DecimalField(max_digits=10, decimal_places=2)
    stock_in = models.IntegerField()
    stock_out = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    agent = models.CharField(max_length=100, help_text=_("The batch/user that made the movement"))

    warehouse = models.ForeignKey(Warehouse)
    good = models.ForeignKey(Good)

    def __str__(self):
        return _("Movement for %s in warehouse %s %s: in %d - out %d") % (
            self.good, self.warehouse, self.stock_field, self.stock_in, self.stock_out)
