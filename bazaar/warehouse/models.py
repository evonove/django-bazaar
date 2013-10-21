from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

import moneyed
from djmoney_rates.utils import convert_money

from ..fields import MoneyField
from ..goods.models import Product
from ..settings import bazaar_settings


@python_2_unicode_compatible
class Stock(models.Model):
    price = MoneyField(help_text=_("Buying unit price for this stock in the system currency"))
    original_price = MoneyField(help_text=_("Buying unit price for this stock in the original "
                                            "currency"))

    code = models.CharField(max_length=100, blank=True)
    product = models.ForeignKey(Product, related_name="stocks")

    def save(self, *args, **kwargs):
        default_currency = moneyed.CURRENCIES[bazaar_settings.DEFAULT_CURRENCY]

        currency = getattr(self.price, "currency", default_currency)
        if currency != default_currency:
            self.original_price = self.price

            self.price = convert_money(self.price.amount, currency.code, default_currency.code)
            self.price.currency = default_currency

        return super(Stock, self).save(*args, **kwargs)

    def __str__(self):
        return _("Stock %s - '%s'") % (self.code, self.product)


@python_2_unicode_compatible
class Movement(models.Model):
    quantity = models.DecimalField(max_digits=30, decimal_places=4)
    date = models.DateTimeField(default=timezone.now)
    agent = models.CharField(max_length=100, help_text=_("The batch/user that made the movement"))
    reason = models.TextField()

    stock = models.ForeignKey(Stock, related_name="movements")

    class Meta:
        get_latest_by = "date"
        ordering = ["-date"]

    def __str__(self):
        return _("Movement %s - %s by %s: %.4f") % (
            self.stock, self.reason, self.agent, self.quantity)
