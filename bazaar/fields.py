from __future__ import absolute_import
from __future__ import unicode_literals

import moneyed
import uuid

from django.db.models import CharField
from djmoney.models.fields import MoneyField as _MoneyField
from functools import partial

from .settings import bazaar_settings


MoneyField = partial(
    _MoneyField, max_digits=30, decimal_places=2,
    default=moneyed.Money(0.0, bazaar_settings.DEFAULT_CURRENCY),
    default_currency=bazaar_settings.DEFAULT_CURRENCY,
    currency_choices=bazaar_settings.CURRENCIES)


class UUIDField(CharField):

    description = 'Field to store UUID values'


def create_uuid():
    return uuid.uuid4().hex
