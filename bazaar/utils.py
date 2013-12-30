from __future__ import unicode_literals

from djmoney_rates.utils import convert_money

import moneyed

from .settings import bazaar_settings


def money_to_default(money):
    """
    Convert money amount to the system default currency. If money has no 'currency' attribute
    does nothing
    """
    if hasattr(money, "currency"):
        default_currency = moneyed.CURRENCIES[bazaar_settings.DEFAULT_CURRENCY]

        if money.currency != default_currency:
            money = convert_money(money.amount, money.currency.code, default_currency.code)

    return money
