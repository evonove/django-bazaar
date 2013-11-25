from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ..fields import MoneyField
from ..goods.models import Product
from ..utils import convert_money_to_default_currency


@python_2_unicode_compatible
class Stock(models.Model):
    price = MoneyField(help_text=_("Buying unit price for this stock in the system currency"))
    original_price = MoneyField(help_text=_("Buying unit price for this stock in the original "
                                            "currency"))

    created = models.DateTimeField(auto_now=True)

    code = models.CharField(max_length=100, blank=True)
    product = models.ForeignKey(Product, related_name="stocks")

    class Meta:
        ordering = ['created']
        get_latest_by = "created"

    @property
    def quantity(self):
        quantity = 0
        for movement in self.movements.all():
            quantity += movement.quantity
        return quantity

    def save(self, *args, **kwargs):
        new_price = convert_money_to_default_currency(self.price)
        if new_price != self.price:
            self.original_price = self.price
            self.price = new_price

        return super(Stock, self).save(*args, **kwargs)

    def __str__(self):
        return _("Stock %s - '%s'") % (self.code or self.price, self.product)


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
