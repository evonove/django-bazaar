from __future__ import unicode_literals

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ..settings import bazaar_settings


@python_2_unicode_compatible
class Warehouse(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Stock(models.Model):
    quantity = models.IntegerField(default=0)

    warehouse = models.ForeignKey(Warehouse, related_name="stocks")

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    good = generic.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return _("Stock for %s in warehouse %s: quantity %d") % (self.good, self.warehouse, self.quantity)


@python_2_unicode_compatible
class Movement(models.Model):
    price_in = models.DecimalField(max_digits=10, decimal_places=2,
                                   help_text=_("Price of a single unit of the movement's good"))
    currency = models.CharField(max_length=3, choices=bazaar_settings.CURRENCIES)

    stock_in = models.IntegerField()
    stock_out = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    agent = models.CharField(max_length=100, help_text=_("The batch/user that made the movement"))

    warehouse = models.ForeignKey(Warehouse)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    good = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        get_latest_by = "date"
        ordering = ["-date"]

    def __str__(self):
        return _("Movement for %s in warehouse %s: in %d - out %d") % (
            self.good, self.warehouse, self.stock_in, self.stock_out)
