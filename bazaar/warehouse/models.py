from __future__ import division
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ..fields import MoneyField
from ..goods.models import Product


@python_2_unicode_compatible
class Location(models.Model):
    LOCATION_SUPPLIER = 0
    LOCATION_STORAGE = 1
    LOCATION_OUTPUT = 2
    LOCATION_CUSTOMER = 3
    LOCATION_LOST_AND_FOUND = 4

    LOCATION_TYPE_CHOICES = (
        (LOCATION_SUPPLIER, _("Supplier")),
        (LOCATION_STORAGE, _("Storage")),
        (LOCATION_OUTPUT, _("Output")),
        (LOCATION_CUSTOMER, _("Customer")),
        (LOCATION_LOST_AND_FOUND, _("Lost And Found")),
    )

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    type = models.IntegerField(choices=LOCATION_TYPE_CHOICES)

    def __str__(self):
        return _("Location %s (%s)") % (self.name, self.get_type_display())


@python_2_unicode_compatible
class Movement(models.Model):
    from_location = models.ForeignKey(Location, related_name="outgoing")
    to_location = models.ForeignKey(Location, related_name="incoming")

    date = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits=30, decimal_places=4)
    unit_price = MoneyField(null=True, help_text=_("Unit price for this movement"))

    agent = models.CharField(max_length=100, blank=True,
                             help_text=_("The batch/user that made the movement"))
    note = models.TextField(blank=True)

    class Meta:
        get_latest_by = "date"
        ordering = ["-date"]

    @property
    def value(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return _("Movement '%s' - %s by %s: %.4f") % (
            self.stock.product, self.reason, self.agent, self.quantity)


@python_2_unicode_compatible
class Stock(models.Model):
    """
    Denormalized stock data for a product in a location.
    TODO: this could be a database view
    """
    product = models.ForeignKey(Product, related_name="stocks")
    location = models.ForeignKey(Location, related_name="stocks")

    unit_price = MoneyField(help_text=_("Average unit price for this stock in the system currency"))
    quantity = models.DecimalField(max_digits=30, decimal_places=4, default=0)

    class Meta:
        unique_together = ('product', 'location')

    @property
    def value(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return _("Stock '%s' at %s: %s") % (self.product, self.location, self.value)
