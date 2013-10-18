from __future__ import unicode_literals

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

import moneyed
from djmoney_rates.utils import convert_money

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

    def save(self, *args, **kwargs):
        default_currency = moneyed.CURRENCIES[bazaar_settings.DEFAULT_CURRENCY]

        currency = getattr(self.price, "currency", default_currency)
        if currency != default_currency:
            self.original_price = self.price

            self.price = convert_money(self.price.amount, currency.code, default_currency.code)
            self.price.currency = default_currency

        return super(RealGood, self).save(*args, **kwargs)

    def __str__(self):
        return _("Real good %s - '%s' in %s") % (self.uid, self.good, self.warehouse)


class PriceListManager(models.Manager):
    use_for_related_fields = True

    def get_default(self):
        """
        Return the default warehouse instance
        """
        try:
            return self.get_query_set().get(pk=bazaar_settings.DEFAULT_WAREHOUSE_ID)
        except Warehouse.DoesNotExist:
            raise ImproperlyConfigured("A default warehouse must exists. Please create one")


@python_2_unicode_compatible
class Warehouse(models.Model):
    name = models.CharField(max_length=100)

    objects = PriceListManager()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Movement(models.Model):
    quantity = models.DecimalField(max_digits=30, decimal_places=4)
    date = models.DateTimeField(default=timezone.now)
    agent = models.CharField(max_length=100, help_text=_("The batch/user that made the movement"))
    reason = models.TextField()

    warehouse = models.ForeignKey(Warehouse)

    good = models.ForeignKey(RealGood, related_name="movements")

    class Meta:
        get_latest_by = "date"
        ordering = ["-date"]

    def __str__(self):
        return _("Movement from %s in warehouse %s: %.4f") % (
            self.agent, self.warehouse, self.quantity)
