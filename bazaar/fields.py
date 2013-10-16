from __future__ import unicode_literals

from functools import partial

from djmoney.models.fields import MoneyField as _MoneyField

from .settings import bazaar_settings


MoneyField = partial(
    _MoneyField, max_digits=30, decimal_places=2,
    default_currency=bazaar_settings.DEFAULT_CURRENCY,
    currency_choices=bazaar_settings.CURRENCIES)
