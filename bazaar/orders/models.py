from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from bazaar.listings.models import Publishing, Store


@python_2_unicode_compatible
class Order(models.Model):
    external_id = models.CharField(max_length=256)
    store = models.ForeignKey(Store)
    publishing = models.ForeignKey(Publishing, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "Order %s from %s" % (self.external_id, self.store)
