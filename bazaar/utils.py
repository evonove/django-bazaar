from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import six

from djmoney_rates.utils import convert_money

from moneyed import Money, get_currency

import stored_messages

from .settings import bazaar_settings


def get_default_currency():
    return get_currency(bazaar_settings.DEFAULT_CURRENCY)


def has_default_currency(money):
    if hasattr(money, "currency"):
        return money.currency == get_default_currency()
    else:
        return True


def money_to_default(value):
    """
    Convert 'value' to the system default currency. Returns a Money instance
    """
    if not has_default_currency(value):
        default_currency = get_default_currency()
        value = convert_money(value.amount, value.currency.code, default_currency.code)

    return to_money(value)


def to_money(value):
    """
    Convert a value to a Money instance. Noop if value is a Money instance.
    """
    if not isinstance(value, Money):
        value = Money(value, get_default_currency())
    return value


def send_to_staff(messages, level=None):
    if not messages:
        return

    level = level or stored_messages.STORED_ERROR

    if isinstance(messages, six.string_types):
        messages = [messages]

    users = get_user_model().objects.filter(is_staff=True)

    for message in messages:
        rendered = render_to_string("bazaar/message.html", {"message": message})
        stored_messages.add_message_for(users, level, rendered)
