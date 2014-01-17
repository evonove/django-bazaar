from __future__ import division
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from bazaar.signals import product_stock_changed

from ..fields import MoneyField
from ..goods.models import Product
from ..utils import money_to_default


@python_2_unicode_compatible
class Stock(models.Model):
    price = MoneyField(help_text=_("Average unit price for this stock in the system currency"))
    product = models.OneToOneField(Product, related_name="stock")
    quantity = models.DecimalField(max_digits=30, decimal_places=4, default=0)

    def save(self, *args, **kwargs):
        self.price = money_to_default(self.price)
        return super(Stock, self).save(*args, **kwargs)

    def __str__(self):
        return _("Stock '%s' - %s") % (self.product, self.price)


@python_2_unicode_compatible
class Movement(models.Model):
    quantity = models.DecimalField(max_digits=30, decimal_places=4)
    date = models.DateTimeField(default=timezone.now)
    agent = models.CharField(max_length=100, help_text=_("The batch/user that made the movement"))
    reason = models.TextField()
    price = MoneyField(null=True, help_text=_("Unit price for this movement"))

    stock = models.ForeignKey(Stock, related_name="movements")

    class Meta:
        get_latest_by = "date"
        ordering = ["-date"]

    def __str__(self):
        return _("Movement '%s' - %s by %s: %.4f") % (
            self.stock.product, self.reason, self.agent, self.quantity)


@receiver(post_save, sender=Movement)
def update_stock_price(sender, instance, created, **kwargs):
    movement = instance
    if created:
        stock = movement.stock

        # compute average price only for incoming movements
        if movement.quantity > 0:
            price = money_to_default(movement.price or 0)

            new_qta = stock.quantity + movement.quantity
            if new_qta > 0:
                avg_price = ((stock.quantity * stock.price + movement.quantity * price) / new_qta)
                stock.price = avg_price

        stock.quantity += movement.quantity
        stock.save()

        product_stock_changed.send(sender=stock, quantity=movement.quantity)
