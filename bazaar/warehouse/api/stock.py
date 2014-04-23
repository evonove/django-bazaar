from __future__ import unicode_literals
from __future__ import division

from django.db.models import Sum

from ...utils import money_to_default
from ..models import Stock


def get_stock_quantity(product, location_type=None, **kwargs):
    qs = Stock.objects.filter(product=product, **kwargs)

    if location_type:
        qs = qs.filter(location__type=location_type)

    result = qs.aggregate(Sum("quantity"))

    return result["quantity__sum"] or 0


def get_stock_price(product, location_type=None, **kwargs):
    qs = Stock.objects.filter(product=product, **kwargs)

    if location_type:
        qs = qs.filter(location__type=location_type)

    stocks = qs.values("unit_price", "quantity")

    if len(stocks) > 0:
        # compute a weighted arithmetic mean or standard mean if weights sum is 0
        weights = sum(map(lambda s: s["quantity"], stocks))
        if weights != 0:
            value = sum(map(lambda s: s["unit_price"] * s["quantity"], stocks)) / weights
        else:
            value = sum(map(lambda s: s["unit_price"], stocks)) / len(stocks)
    else:
        value = 0

    return money_to_default(value)
