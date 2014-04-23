from __future__ import unicode_literals
from __future__ import division

from django.db.models import Sum

from ..models import Stock


def get_stock_quantity(product, location_type=None, **kwargs):
    qs = Stock.objects.filter(product=product, **kwargs)

    if location_type:
        qs = qs.filter(location__type=location_type)

    result = qs.aggregate(Sum("quantity"))

    return result["quantity__sum"]


def get_stock_price(product, location_type=None, **kwargs):
    qs = Stock.objects.filter(product=product, **kwargs)

    if location_type:
        qs = qs.filter(location__type=location_type)

    stocks = qs.values("unit_price", "quantity")

    # compute Weighted arithmetic mean
    values = sum(map(lambda s: s["unit_price"] * s["quantity"], stocks))
    weights = sum(map(lambda s: s["quantity"], stocks))

    if weights != 0:
        return values / weights
    else:
        return 0