from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from bazaar.listings.models import Publishing, Store


@python_2_unicode_compatible
class Order(models.Model):
    ORDER_PENDING = 0
    ORDER_COMPLETED = 1
    ORDER_STATUS_CHOICES = (
        (ORDER_PENDING, "Pending"),
        (ORDER_COMPLETED, "Completed"),
    )
    external_id = models.CharField(max_length=256)
    store = models.ForeignKey(Store)
    publishing = models.ForeignKey(Publishing, null=True, blank=True)

    quantity = models.IntegerField(default=1)

    status = models.IntegerField(max_length=50, choices=ORDER_STATUS_CHOICES, default=ORDER_PENDING)

    def __str__(self):
        return "Order %s from %s" % (self.external_id, self.store)
