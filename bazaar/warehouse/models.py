from __future__ import unicode_literals

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ..settings import bazaar_settings
from ..fields import MoneyField


@python_2_unicode_compatible
class RealGood(models.Model):
    price = MoneyField(help_text=_("Buying unit price for this good in the system currency"))
    original_price = MoneyField(help_text=_("Buying unit price for this good in the original currency"))

    uid = models.CharField(max_length=500, blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    good = generic.GenericForeignKey('content_type', 'object_id')

    warehouse = models.ForeignKey("Warehouse")

    def clean(self):
        if self.price.currency.code != bazaar_settings.DEFAULT_CURRENCY:
            raise ValidationError("Price field must contain prices in the system currency."
                                  "Store the price with in the original currency in original_price field")

    def __str__(self):
        return _("Real good %s - %s in %s") % (self.uid, self.good, self.warehouse)


@python_2_unicode_compatible
class Warehouse(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Movement(models.Model):
    quantity = models.DecimalField(max_digits=30, decimal_places=4)
    date = models.DateTimeField(default=timezone.now)
    agent = models.CharField(max_length=100, help_text=_("The batch/user that made the movement"))

    warehouse = models.ForeignKey(Warehouse)

    good = models.ForeignKey(RealGood, related_name="movements")

    class Meta:
        get_latest_by = "date"
        ordering = ["-date"]

    def __str__(self):
        return _("Movement from %s in warehouse %s: %d") % (
            self.agent, self.warehouse, self.quantity)
